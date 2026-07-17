from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from bokhald.models import Bokhaldslykill, Faersla, Maelabord, SuperAdminKerfiskaupandi
from reikningar.models import FasturLidur, Greidsla, Reikningur, ReikningsLidur
from starfsfolk.models import Fridagur, Maeting, Notandi, Serhaefi, Starfsmadur, Vinnukostnadur
from verkefni.models import DeadlineAminnning, Verkbeiðni, Verkefni, VerkefniAthugasemd, VerkefniSkra
from vidskiptavinir.models import Kerfisnumer, Vidskiptavinur


class Command(BaseCommand):
    help = "Býr til raunhæf tengd beta-prófunargögn í öllum kerfum."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default="BetaTest!2026",
            help="Lykilorð sem verður sett á alla nýja test-notendur.",
        )

    def handle(self, *args, **options):
        password = options["password"]

        with transaction.atomic():
            users = self._seed_users(password=password)
            staff = self._seed_staff(users)
            customers = self._seed_customers()
            project_data = self._seed_projects(users, staff, customers)
            invoice_data = self._seed_invoices(users, customers, project_data)
            self._seed_accounting(users, staff, customers, invoice_data)
            self._seed_superadmin_company(users)
            self._seed_dashboard(users)

        self.stdout.write(self.style.SUCCESS("Beta-prófunargögn tilbúin."))
        self.stdout.write("Innskráningar (lykill fyrir nýja notendur):")
        self.stdout.write(f"- super.beta / {password}")
        self.stdout.write(f"- sub.beta / {password}")
        self.stdout.write(f"- anna.d / {password}")
        self.stdout.write(f"- bjorn.s / {password}")
        self.stdout.write(f"- katrin.o / {password}")

    def _seed_users(self, password):
        users = {}

        users["super"] = self._upsert_user(
            username="super.beta",
            email="superadmin@isafoldlausnir.is",
            full_name="Sigrun Einarsdottir",
            phone="6991122",
            user_type="SUPER_ADMIN",
            is_admin=True,
            is_staff_member=True,
            is_superuser=True,
            password=password,
        )

        users["sub"] = self._upsert_user(
            username="sub.beta",
            email="rekstur@isafoldlausnir.is",
            full_name="Aron Kristjansson",
            phone="7763321",
            user_type="SUB_ADMIN",
            is_admin=True,
            is_staff_member=True,
            is_superuser=False,
            password=password,
        )

        users["anna"] = self._upsert_user(
            username="anna.d",
            email="anna@isafoldlausnir.is",
            full_name="Anna Dora Sigurdardottir",
            phone="8451100",
            user_type="STARFSMADUR",
            is_admin=False,
            is_staff_member=True,
            is_superuser=False,
            password=password,
        )

        users["bjorn"] = self._upsert_user(
            username="bjorn.s",
            email="bjorn@isafoldlausnir.is",
            full_name="Bjorn Steinar Magnusson",
            phone="8672201",
            user_type="STARFSMADUR",
            is_admin=False,
            is_staff_member=True,
            is_superuser=False,
            password=password,
        )

        users["katrin"] = self._upsert_user(
            username="katrin.o",
            email="katrin@isafoldlausnir.is",
            full_name="Katrin Olafia Jonsdottir",
            phone="8654402",
            user_type="STARFSMADUR",
            is_admin=False,
            is_staff_member=True,
            is_superuser=False,
            password=password,
        )

        return users

    def _seed_staff(self, users):
        serhaefi_names = [
            ("Rafmagn", "Uppsetning og bilanagreining rafmagnskerfa."),
            ("Netkerfi", "Uppsetning eldveggja, rofa og innri neta."),
            ("Notendaþjonusta", "Dagleg þjónusta við notendur og rekstur."),
            ("Bokhaldskerfi", "Innleiðing og rekstur fjárhagskerfa."),
        ]
        serhaefi_map = {}
        for name, description in serhaefi_names:
            serhaefi_obj, _ = Serhaefi.objects.get_or_create(
                heiti=name,
                defaults={"lysing": description},
            )
            serhaefi_map[name] = serhaefi_obj

        staff_profiles = {}
        staff_profiles["anna"] = self._upsert_staff_profile(
            user=users["anna"],
            kennitala="120890-3129",
            address="Austurbrun 12, 104 Reykjavik",
            phone="8451100",
            ad_user="ANNA.SIGURDARDOTTIR",
            arrival=time(8, 0),
            departure=time(16, 0),
            serhaefi=[serhaefi_map["Rafmagn"], serhaefi_map["Notendaþjonusta"]],
        )
        staff_profiles["bjorn"] = self._upsert_staff_profile(
            user=users["bjorn"],
            kennitala="220585-4419",
            address="Laugavegur 72, 101 Reykjavik",
            phone="8672201",
            ad_user="BJORN.MAGNUSSON",
            arrival=time(7, 30),
            departure=time(15, 30),
            serhaefi=[serhaefi_map["Netkerfi"]],
        )
        staff_profiles["katrin"] = self._upsert_staff_profile(
            user=users["katrin"],
            kennitala="031192-2899",
            address="Myrargata 21, 101 Reykjavik",
            phone="8654402",
            ad_user="KATRIN.JONSDOTTIR",
            arrival=time(9, 0),
            departure=time(17, 0),
            serhaefi=[serhaefi_map["Bokhaldskerfi"], serhaefi_map["Notendaþjonusta"]],
        )

        today = timezone.localdate()
        recent_days = [today - timedelta(days=d) for d in range(5)]

        for day in recent_days:
            for staff_key, status in (("anna", "MAETTUR"), ("bjorn", "MAETTUR"), ("katrin", "FJARVERANDI" if day.weekday() == 0 else "MAETTUR")):
                moett = timezone.make_aware(datetime.combine(day, time(8, 15)))
                brott = timezone.make_aware(datetime.combine(day, time(16, 5)))
                defaults = {
                    "status": status,
                    "moettartimi": moett if status == "MAETTUR" else None,
                    "brottfararstimi": brott if status == "MAETTUR" else None,
                    "athugasemdir": "Sjalfvirk beta skraning fyrir matskeyrslu.",
                }
                Maeting.objects.update_or_create(
                    starfsmadur=staff_profiles[staff_key],
                    dagsetning=day,
                    defaults=defaults,
                )

        Fridagur.objects.update_or_create(
            starfsmadur=staff_profiles["katrin"],
            fra_dagsetning=today + timedelta(days=7),
            til_dagsetning=today + timedelta(days=9),
            defaults={
                "fridags_tegund": "ORLOF",
                "lysing": "Skipulagt vetrarfrí með fjölskyldu.",
                "stada": "SAMTHYKKTUR",
                "samthykkt_af": users["sub"],
            },
        )

        Vinnukostnadur.objects.update_or_create(
            starfsmadur=staff_profiles["anna"],
            dagsetning=today - timedelta(days=3),
            kostnadar_tegund="LAUN",
            defaults={
                "fjarhaed": Decimal("84500.00"),
                "lysing": "Vikulaun fyrir vettvangsverkefni.",
                "er_greitt": True,
            },
        )

        Vinnukostnadur.objects.update_or_create(
            starfsmadur=staff_profiles["bjorn"],
            dagsetning=today - timedelta(days=2),
            kostnadar_tegund="EFNISKOSTNADUR",
            defaults={
                "fjarhaed": Decimal("32600.00"),
                "lysing": "Netrofi, patch panel og cat6 efni.",
                "er_greitt": False,
            },
        )

        return staff_profiles

    def _seed_customers(self):
        customers = {}

        customers["orka"] = self._upsert_customer(
            name="Orka & Gagn Lausnir ehf.",
            kennitala="640915-0100",
            address="Borgartun 30, 105 Reykjavik",
            phone="5881100",
            email="innkaup@orkaoggagn.is",
            vsk="145678",
            debt=Decimal("240500.00"),
            notes="Langtimasamningur um rekstur og utköll.",
        )
        customers["fiskur"] = self._upsert_customer(
            name="Fiskvinnslan Bru ehf.",
            kennitala="570101-2290",
            address="Hafnargata 4, 230 Reykjanesbaer",
            phone="4213300",
            email="bokhald@fiskvinnslanbru.is",
            vsk="198765",
            debt=Decimal("0.00"),
            notes="Greiðir innan 14 daga, krefst sundurliðunar i reikningum.",
        )
        customers["verslun"] = self._upsert_customer(
            name="Verslun Midbæjar slf.",
            kennitala="511298-3049",
            address="Aðalstraeti 9, 600 Akureyri",
            phone="4624400",
            email="rekstur@verslunmidbaejar.is",
            vsk="112233",
            debt=Decimal("87500.00"),
            notes="Nyr viðskiptavinur með vaxandi verkefni.",
        )

        Kerfisnumer.objects.update_or_create(
            item_id="ITM-OG-2026-001",
            defaults={
                "vidskiptavinur": customers["orka"],
                "lysing": "Eldveggur i gagnaveri + eftirlitskerfi.",
                "er_virkur": True,
            },
        )
        Kerfisnumer.objects.update_or_create(
            item_id="ITM-FB-2026-017",
            defaults={
                "vidskiptavinur": customers["fiskur"],
                "lysing": "Uppfaersla a framleiðsluneti i vinnsluhúsi.",
                "er_virkur": True,
            },
        )
        Kerfisnumer.objects.update_or_create(
            item_id="ITM-VM-2026-004",
            defaults={
                "vidskiptavinur": customers["verslun"],
                "lysing": "POS kerfi og rekjanleiki fyrir lager.",
                "er_virkur": True,
            },
        )

        return customers

    def _seed_projects(self, users, staff, customers):
        today = timezone.now()
        data = {}

        request_fw, _ = Verkbeiðni.objects.update_or_create(
            vidskiptavinur=customers["orka"],
            titill="Eldveggur og netvöktun i höfuðstöðvum",
            defaults={
                "lysing": "Skipta ut eldri eldvegg, setja SIEM tengingu og 24/7 netvöktun.",
                "forgangur": "HEIUR",
                "stada": "I_VINNSLU",
                "stofnad_af": users["sub"],
                "samthykkt_af": users["super"],
            },
        )

        request_finance, _ = Verkbeiðni.objects.update_or_create(
            vidskiptavinur=customers["fiskur"],
            titill="Samþætting bókhaldskerfis við birgðakerfi",
            defaults={
                "lysing": "Tengja daglegar birgðahreyfingar við bókhald og reikningagerð.",
                "forgangur": "MIDLUNGS",
                "stada": "SAMTHYKKTUR",
                "stofnad_af": users["sub"],
                "samthykkt_af": users["super"],
            },
        )

        project_fw, _ = Verkefni.objects.update_or_create(
            verkbeidni=request_fw,
            titill="Innleiðing eldveggs FortiGate",
            defaults={
                "starfsmadur": staff["bjorn"],
                "lysing": "Setja upp VLAN, policy-reglur, VPN og atburðaskraningu.",
                "stada": "I_VINNSLU",
                "vinnustadur": "VINNUSTADUR",
                "deadline": today + timedelta(days=5),
                "uthlutad_af": users["sub"],
            },
        )

        project_support, _ = Verkefni.objects.update_or_create(
            verkbeidni=request_fw,
            titill="Notendaþjonusta eftir netbreytingar",
            defaults={
                "starfsmadur": staff["anna"],
                "lysing": "Stilla endpoint varnir, aðgang og fræða notendur.",
                "stada": "OBIDINN",
                "vinnustadur": "UTKALL",
                "deadline": today + timedelta(days=8),
                "uthlutad_af": users["sub"],
            },
        )

        project_finance, _ = Verkefni.objects.update_or_create(
            verkbeidni=request_finance,
            titill="API tenging bokhalds og birgðakerfis",
            defaults={
                "starfsmadur": staff["katrin"],
                "lysing": "Byggja tvíátta samþættingu, validera færslur og keyra UAT.",
                "stada": "I_VINNSLU",
                "vinnustadur": "VINNUSTADUR",
                "deadline": today + timedelta(days=12),
                "uthlutad_af": users["sub"],
            },
        )

        for project, user, note in (
            (project_fw, users["bjorn"], "Stillingar klárar, test VPN virkar fyrir tvo staði."),
            (project_support, users["anna"], "Bið eftir staðfestingu á glugga fyrir vettvangsferð."),
            (project_finance, users["katrin"], "UAT gagnamengi tilbúið og tengi prófað i staging."),
        ):
            VerkefniAthugasemd.objects.update_or_create(
                verkefni=project,
                notandi=user,
                athugasemd=note,
            )

        for project, reminder_days in ((project_fw, 2), (project_finance, 3), (project_support, 1)):
            DeadlineAminnning.objects.update_or_create(
                verkefni=project,
                aminntar_dagar_fyrir=reminder_days,
                defaults={"send_aminningu": True},
            )

        VerkefniSkra.objects.update_or_create(
            verkefni=project_fw,
            lysing="Uppsetningarskjal - beta",
            defaults={
                "skra": "verkefni_skrar/uppsetningarskjal-beta.txt",
                "tegund": "SKJAL",
                "upphlad_af": users["bjorn"],
            },
        )

        data["fw"] = project_fw
        data["support"] = project_support
        data["finance"] = project_finance
        return data

    def _seed_invoices(self, users, customers, project_data):
        fastur_voktun, _ = FasturLidur.objects.update_or_create(
            heiti="Manadarleg netvöktun",
            defaults={
                "lysing": "24/7 eftirlit með neti, viðvaranir og mánaðarskýrsla.",
                "fjarhaed": Decimal("59000.00"),
                "er_virkur": True,
            },
        )
        fastur_leyfi, _ = FasturLidur.objects.update_or_create(
            heiti="Öryggisleyfi og endpoint vörn",
            defaults={
                "lysing": "Leyfiskostnaður fyrir endpoint og eldveggsvörn.",
                "fjarhaed": Decimal("34500.00"),
                "er_virkur": True,
            },
        )

        today = timezone.localdate()
        invoices = {}

        inv_orka, _ = Reikningur.objects.update_or_create(
            vidskiptavinur=customers["orka"],
            athugasemdir="Mars 2026 þjónusta og netvöktun.",
            defaults={
                "verkefni": project_data["fw"],
                "reikningsdagsetning": today - timedelta(days=2),
                "gjalddagi": today + timedelta(days=12),
                "eindagi": today + timedelta(days=18),
                "stada": "SENDUR",
                "er_greiddur": False,
                "stofnad_af": users["sub"],
            },
        )

        inv_fiskur, _ = Reikningur.objects.update_or_create(
            vidskiptavinur=customers["fiskur"],
            athugasemdir="Innleiðing API og gögn fyrir UAT.",
            defaults={
                "verkefni": project_data["finance"],
                "reikningsdagsetning": today - timedelta(days=10),
                "gjalddagi": today - timedelta(days=1),
                "eindagi": today + timedelta(days=5),
                "stada": "GREIDDUR",
                "er_greiddur": True,
                "stofnad_af": users["sub"],
            },
        )

        self._sync_invoice_lines(
            inv_orka,
            [
                ("Vettvangsvinna netuppsetning", Decimal("22"), Decimal("11500.00"), "VINNUKOSTNADUR"),
                (fastur_voktun.heiti, Decimal("1"), fastur_voktun.fjarhaed, "FASTUR_LIDUR"),
                (fastur_leyfi.heiti, Decimal("1"), fastur_leyfi.fjarhaed, "FASTUR_LIDUR"),
            ],
        )

        self._sync_invoice_lines(
            inv_fiskur,
            [
                ("API hönnun og forritun", Decimal("18"), Decimal("12600.00"), "VINNUKOSTNADUR"),
                ("Test gagnamengi og samanburður", Decimal("1"), Decimal("45000.00"), "ANNAD"),
            ],
        )

        Greidsla.objects.update_or_create(
            reikningur=inv_fiskur,
            greidsludagsetning=today,
            fjarhaed=inv_fiskur.heildarfjarhaed,
            defaults={
                "greidslu_adferd": "MILLIFAERSLA",
                "athugasemdir": "Greitt i einni millifaerslu.",
                "skrad_af": users["sub"],
            },
        )

        invoices["orka"] = inv_orka
        invoices["fiskur"] = inv_fiskur
        return invoices

    def _seed_accounting(self, users, staff, customers, invoice_data):
        account_defs = [
            ("1010", "Banki", "EIGNIR", "Bankareikningur fyrirtækis"),
            ("1200", "Viðskiptakröfur", "EIGNIR", "Ógreiddir reikningar viðskiptavina"),
            ("3000", "Þjónustutekjur", "TEKJUR", "Tekjur af þjónustuverkefnum"),
            ("4010", "Launakostnaður", "GJOLD", "Laun og tengdur kostnaður"),
            ("4500", "Efniskostnaður", "GJOLD", "Efniskostnaður og búnaður"),
        ]
        accounts = {}
        for number, title, kind, description in account_defs:
            account, _ = Bokhaldslykill.objects.update_or_create(
                lykilnumer=number,
                defaults={"heiti": title, "tegund": kind, "lysing": description, "er_virkur": True},
            )
            accounts[number] = account

        today = date.today()

        Faersla.objects.update_or_create(
            dagsetning=today - timedelta(days=2),
            lysing="Tekjufærsla vegna reiknings Orka & Gagn",
            bokhaldslykill=accounts["3000"],
            defaults={
                "debet_fjarhaed": Decimal("0.00"),
                "kredit_fjarhaed": invoice_data["orka"].heildarfjarhaed,
                "fjarhaed": invoice_data["orka"].heildarfjarhaed,
                "tegund": "TEKJUR",
                "flokkur": "REIKNINGUR",
                "vidskiptavinur": customers["orka"],
                "starfsmadur": staff["anna"],
                "athugasemdir": "Ógreidd krafa á þjónustusamning.",
                "skrad_af": users["sub"],
            },
        )

        Faersla.objects.update_or_create(
            dagsetning=today - timedelta(days=1),
            lysing="Greiðsla inn á banka vegna Fiskvinnslunnar Brú",
            bokhaldslykill=accounts["1010"],
            defaults={
                "debet_fjarhaed": invoice_data["fiskur"].heildarfjarhaed,
                "kredit_fjarhaed": Decimal("0.00"),
                "fjarhaed": invoice_data["fiskur"].heildarfjarhaed,
                "tegund": "TEKJUR",
                "flokkur": "REIKNINGUR",
                "vidskiptavinur": customers["fiskur"],
                "starfsmadur": staff["katrin"],
                "athugasemdir": "Greiðsla staðfest og bókuð í banka.",
                "skrad_af": users["sub"],
            },
        )

        Faersla.objects.update_or_create(
            dagsetning=today - timedelta(days=3),
            lysing="Laun og yfirvinna fyrir vettvangsteymi",
            bokhaldslykill=accounts["4010"],
            defaults={
                "debet_fjarhaed": Decimal("84500.00"),
                "kredit_fjarhaed": Decimal("0.00"),
                "fjarhaed": Decimal("84500.00"),
                "tegund": "GJOLD",
                "flokkur": "LAUN",
                "vidskiptavinur": customers["orka"],
                "starfsmadur": staff["anna"],
                "athugasemdir": "Vikulegur launakostnaður úthlutaður á verkefni.",
                "skrad_af": users["sub"],
            },
        )

    def _seed_superadmin_company(self, users):
        SuperAdminKerfiskaupandi.objects.update_or_create(
            kennitala="640915-0100",
            defaults={
                "fyrirtaeki_nafn": "Isafold Lausnir ehf.",
                "abyrgdarmaður": "Aron Kristjansson",
                "netfang": "rekstur@isafoldlausnir.is",
                "heimilisfang": "Borgartun 30",
                "postnumer": "105",
                "land": "Island",
                "simanumer": "5881100",
                "sub_admin_notandi": users["sub"],
                "er_virkur": True,
                "athugasemdir": "Beta tenant fyrir prófanir á super-admin launch flow.",
            },
        )

    def _seed_dashboard(self, users):
        today = timezone.localdate()

        Maelabord.objects.update_or_create(
            notandi=users["sub"],
            dagsetning=today,
            defaults={
                "fjoldi_maettra": 2,
                "fjoldi_verkefna_i_vinnslu": 2,
                "fjoldi_verkefna_lokid": 0,
                "heildar_tekjur": Decimal("643700.00"),
                "heildar_gjold": Decimal("117100.00"),
            },
        )

        Maelabord.objects.update_or_create(
            notandi=users["super"],
            dagsetning=today,
            defaults={
                "fjoldi_maettra": 2,
                "fjoldi_verkefna_i_vinnslu": 2,
                "fjoldi_verkefna_lokid": 0,
                "heildar_tekjur": Decimal("643700.00"),
                "heildar_gjold": Decimal("117100.00"),
            },
        )

    def _upsert_user(
        self,
        username,
        email,
        full_name,
        phone,
        user_type,
        is_admin,
        is_staff_member,
        is_superuser,
        password,
    ):
        user, created = Notandi.objects.get_or_create(
            notandanafn=username,
            defaults={
                "email": email,
                "fullt_nafn": full_name,
                "simanumer": phone,
                "notendategund": user_type,
                "er_virkur": True,
                "er_starfsmadur": is_staff_member,
                "er_admin": is_admin,
                "is_superuser": is_superuser,
            },
        )

        if not created:
            user.email = email
            user.fullt_nafn = full_name
            user.simanumer = phone
            user.notendategund = user_type
            user.er_virkur = True
            user.er_starfsmadur = is_staff_member
            user.er_admin = is_admin
            user.is_superuser = is_superuser

        user.set_password(password)
        user.save()
        return user

    def _upsert_staff_profile(self, user, kennitala, address, phone, ad_user, arrival, departure, serhaefi):
        profile, _ = Starfsmadur.objects.update_or_create(
            notandi=user,
            defaults={
                "kennitala": kennitala,
                "heimilisfang": address,
                "simanumer": phone,
                "active_directory_notandi": ad_user,
                "qr_kodi": f"qr_codes/placeholder_{user.notandanafn}.png",
                "aeskilegur_moettartimi": arrival,
                "aeskilegur_brottfararstimi": departure,
                "er_virkur": True,
            },
        )
        profile.serhaefi.set(serhaefi)
        return profile

    def _upsert_customer(self, name, kennitala, address, phone, email, vsk, debt, notes):
        customer, _ = Vidskiptavinur.objects.update_or_create(
            kennitala=kennitala,
            defaults={
                "nafn": name,
                "heimilisfang": address,
                "simanumer": phone,
                "netfang": email,
                "vsk_numer": vsk,
                "skuldastada": debt,
                "er_virkur": True,
                "athugasemdir": notes,
            },
        )
        return customer

    def _sync_invoice_lines(self, invoice, line_specs):
        ReikningsLidur.objects.filter(reikningur=invoice).delete()

        for description, qty, unit_price, line_type in line_specs:
            ReikningsLidur.objects.create(
                reikningur=invoice,
                lysing=description,
                magn=qty,
                einingarverð=unit_price,
                heildarfjarhaed=qty * unit_price,
                tegund=line_type,
            )

        total = sum((qty * unit_price for _, qty, unit_price, _ in line_specs), Decimal("0.00"))
        vat = (total * Decimal("0.24")).quantize(Decimal("0.01"))
        invoice.heildarfjarhaed = total
        invoice.vsk_fjarhaed = vat
        invoice.save(update_fields=["heildarfjarhaed", "vsk_fjarhaed", "uppfaert"])
