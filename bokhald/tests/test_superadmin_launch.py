from django.urls import reverse
from django.core.cache import cache
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase

from bokhald.models import SuperAdminKerfiskaupandi
from starfsfolk.models import Notandi


class SuperAdminLaunchFlowTests(APITestCase):
    def setUp(self):
        cache.clear()

        self.super_admin = Notandi.objects.create_user(
            notandanafn='superadmin',
            email='super@example.com',
            fullt_nafn='Super Admin',
            password='secret123',
            notendategund='SUPER_ADMIN',
            er_admin=True,
            er_starfsmadur=True,
        )

        self.sub_admin = Notandi.objects.create_user(
            notandanafn='subadmin',
            email='sub@example.com',
            fullt_nafn='Sub Admin',
            password='secret123',
            notendategund='SUB_ADMIN',
            er_admin=True,
            er_starfsmadur=True,
        )

        self.kerfiskaupandi = SuperAdminKerfiskaupandi.objects.create(
            fyrirtaeki_nafn='Demo ehf',
            kennitala='1234567890',
            abyrgdarmaður='Jon Test',
            netfang='demo@example.com',
            simanumer='5550000',
            sub_admin_notandi=self.sub_admin,
            er_virkur=True,
        )

    def test_opna_kerfi_returns_one_time_launch_code_by_default(self):
        self.client.force_authenticate(user=self.super_admin)
        url = reverse('kerfiskaupandi-opna-kerfi', args=[self.kerfiskaupandi.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['delivery'], 'code')
        self.assertIn('launch_code', response.data)
        self.assertIn('launch_code=', response.data['launch_url'])

    def test_consume_launch_code_is_single_use(self):
        self.client.force_authenticate(user=self.super_admin)
        opna_url = reverse('kerfiskaupandi-opna-kerfi', args=[self.kerfiskaupandi.id])
        opna_response = self.client.get(opna_url)
        launch_code = opna_response.data['launch_code']

        consume_url = reverse('kerfiskaupandi-consume-launch-code')
        first = self.client.post(consume_url, {'launch_code': launch_code}, format='json')
        second = self.client.post(consume_url, {'launch_code': launch_code}, format='json')

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', first.data)
        self.assertIn('refresh_token', first.data)

        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('villa', second.data)

    def test_non_superadmin_cannot_open_kerfi(self):
        self.client.force_authenticate(user=self.sub_admin)
        url = reverse('kerfiskaupandi-opna-kerfi', args=[self.kerfiskaupandi.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delivery_token_mode_remains_available(self):
        self.client.force_authenticate(user=self.super_admin)
        url = reverse('kerfiskaupandi-opna-kerfi', args=[self.kerfiskaupandi.id])

        response = self.client.get(url, {'delivery': 'token'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['delivery'], 'token')
        self.assertNotIn('launch_code', response.data)
        self.assertIn('access_token=', response.data['launch_url'])

    def test_item_id_is_auto_generated_in_expected_format(self):
        self.assertIsNotNone(self.kerfiskaupandi.item_id)
        self.assertRegex(self.kerfiskaupandi.item_id, r'^KD-W-[A-Z0-9]{11}$')

    def test_item_id_is_unique_between_kerfiskaupendur(self):
        annar = SuperAdminKerfiskaupandi.objects.create(
            fyrirtaeki_nafn='Annað ehf',
            kennitala='9876543210',
            abyrgdarmaður='Anna Test',
            netfang='anna@example.com',
            simanumer='5551111',
            sub_admin_notandi=self.sub_admin,
            er_virkur=True,
        )

        self.assertNotEqual(self.kerfiskaupandi.item_id, annar.item_id)
        self.assertRegex(annar.item_id, r'^KD-W-[A-Z0-9]{11}$')

    def test_kennitala_is_auto_formatted_with_dash(self):
        self.assertEqual(self.kerfiskaupandi.kennitala, '123456-7890')

    def test_postnumer_autofills_sveitarfelag_for_iceland(self):
        kaupandi = SuperAdminKerfiskaupandi.objects.create(
            fyrirtaeki_nafn='Postnumer ehf',
            kennitala='1111112222',
            abyrgdarmaður='Post Test',
            netfang='post@example.com',
            simanumer='5552222',
            postnumer='220',
            land='Island',
            sub_admin_notandi=self.sub_admin,
            er_virkur=True,
        )
        self.assertEqual(kaupandi.sveitarfelag, 'Hafnarfjordur')
        self.assertEqual(kaupandi.landsnumer, '+354')

    def test_phone_length_validation_uses_selected_country(self):
        with self.assertRaises(ValidationError):
            SuperAdminKerfiskaupandi.objects.create(
                fyrirtaeki_nafn='US ehf',
                kennitala='2222223333',
                abyrgdarmaður='US Test',
                netfang='us@example.com',
                simanumer='5552222',  # of stutt fyrir +1 reglur
                land='Bandarikin',
                sub_admin_notandi=self.sub_admin,
                er_virkur=True,
            )
