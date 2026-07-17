from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from starfsfolk.models import (
    Notandi,
    Starfsmadur,
    TimaklukkuAtburdur,
    TimaklukkuLeidretting,
    TimaklukkuTaeki,
)


class TimekeepingFlowTests(APITestCase):
    def setUp(self):
        self.employee_user = Notandi.objects.create_user(
            notandanafn='starfsmadur',
            email='employee@example.com',
            fullt_nafn='Demo Starfsmadur',
            password='secret123',
            notendategund='STARFSMADUR',
            er_starfsmadur=True,
        )
        self.employee = Starfsmadur.objects.create(
            notandi=self.employee_user,
            kennitala='1111111111',
            heimilisfang='Demo gata 1',
            simanumer='5550001',
            starfstitill='Demo',
            qr_kodi='qr_codes/demo.png',
        )
        self.manager_user = Notandi.objects.create_user(
            notandanafn='manager',
            email='manager@example.com',
            fullt_nafn='Demo Manager',
            password='secret123',
            notendategund='SUB_ADMIN',
            er_admin=True,
            er_starfsmadur=True,
        )

    def test_mobile_device_clock_flow_records_status_and_events(self):
        self.client.force_authenticate(user=self.employee_user)

        create_device = self.client.post(
            reverse('timaklukku-taeki-list'),
            {'device_label': 'iPhone demo'},
            format='json',
        )
        self.assertEqual(create_device.status_code, status.HTTP_201_CREATED)
        self.assertIn('pairing_code', create_device.data)

        device = TimaklukkuTaeki.objects.get(id=create_device.data['id'])
        self.assertEqual(device.status, 'PAIRING')
        self.assertNotEqual(device.pairing_code_hash, create_device.data['pairing_code'])

        rejected_connect = self.client.post(
            reverse('timaklukku-taeki-connect', args=[device.id]),
            {'pairing_code': 'wrong-code'},
            format='json',
        )
        self.assertEqual(rejected_connect.status_code, status.HTTP_400_BAD_REQUEST)
        device.refresh_from_db()
        self.assertEqual(device.status, 'PAIRING')

        connect = self.client.post(
            reverse('timaklukku-taeki-connect', args=[device.id]),
            {'pairing_code': create_device.data['pairing_code']},
            format='json',
        )
        self.assertEqual(connect.status_code, status.HTTP_200_OK)
        device.refresh_from_db()
        self.assertEqual(device.status, 'ACTIVE')

        clock_in = self.client.post(
            reverse('maeting-stimplast-inn'),
            {'taeki': device.id},
            format='json',
        )
        self.assertEqual(clock_in.status_code, status.HTTP_200_OK)

        current = self.client.get(reverse('maeting-current-status'))
        self.assertEqual(current.status_code, status.HTTP_200_OK)
        self.assertTrue(current.data['is_clocked_in'])
        self.assertEqual(current.data['active_device_count'], 1)

        clock_out = self.client.post(
            reverse('maeting-stimplast-ut'),
            {'taeki': device.id},
            format='json',
        )
        self.assertEqual(clock_out.status_code, status.HTTP_200_OK)

        history = self.client.get(reverse('maeting-history'))
        self.assertEqual(history.status_code, status.HTTP_200_OK)
        event_types = [row['event_type'] for row in history.data]
        self.assertIn('DEVICE_CONNECTED', event_types)
        self.assertIn('IN', event_types)
        self.assertIn('OUT', event_types)

    def test_mobile_ingest_is_idempotent_for_replayed_client_event(self):
        self.client.force_authenticate(user=self.employee_user)

        create_device = self.client.post(
            reverse('timaklukku-taeki-list'),
            {'device_label': 'Bixby phone'},
            format='json',
        )
        device_id = create_device.data['id']
        self.client.post(
            reverse('timaklukku-taeki-connect', args=[device_id]),
            {'pairing_code': create_device.data['pairing_code']},
            format='json',
        )

        payload = {
            'taeki': device_id,
            'event_type': 'IN',
            'source': 'BIXBY',
            'client_event_id': 'bixby-demo-evt-001',
            'timestamp': '2026-07-17T09:10:00Z',
            'note': 'Voice command clock in',
        }
        first = self.client.post(
            reverse('maeting-mobile-ingest'),
            payload,
            format='json',
        )
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertFalse(first.data['idempotent_replay'])

        replay = self.client.post(
            reverse('maeting-mobile-ingest'),
            payload,
            format='json',
        )
        self.assertEqual(replay.status_code, status.HTTP_200_OK)
        self.assertTrue(replay.data['idempotent_replay'])
        self.assertEqual(first.data['event']['id'], replay.data['event']['id'])
        self.assertEqual(
            TimaklukkuAtburdur.objects.filter(client_event_id='bixby-demo-evt-001').count(),
            1,
        )

    def test_correction_request_can_be_approved_by_manager(self):
        self.client.force_authenticate(user=self.employee_user)
        correction_response = self.client.post(
            reverse('timaklukku-leidretting-list'),
            {
                'requested_change': 'Gleymdi utstimplun kl. 16:05',
                'reason': 'Var ad loka verslun',
            },
            format='json',
        )
        self.assertEqual(correction_response.status_code, status.HTTP_201_CREATED)

        correction = TimaklukkuLeidretting.objects.get(id=correction_response.data['id'])
        self.assertEqual(correction.status, 'PENDING')
        self.assertTrue(
            TimaklukkuAtburdur.objects.filter(
                starfsmadur=self.employee,
                event_type='CORRECTION_REQUESTED',
            ).exists()
        )

        self.client.force_authenticate(user=self.manager_user)
        approve_response = self.client.post(
            reverse('timaklukku-leidretting-approve', args=[correction.id]),
            {'manager_note': 'Samthykkt eftir yfirferd'},
            format='json',
        )
        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)

        correction.refresh_from_db()
        self.assertEqual(correction.status, 'APPROVED')
        self.assertEqual(correction.reviewed_by, self.manager_user)
        self.assertTrue(
            TimaklukkuAtburdur.objects.filter(
                starfsmadur=self.employee,
                event_type='CORRECTION_APPROVED',
            ).exists()
        )
