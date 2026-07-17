from rest_framework import serializers
from .models import Faersla, SuperAdminKerfiskaupandi, Maelabord, Bokhaldslykill


class BokhaldslykillSerializer(serializers.ModelSerializer):
    yfirlykilnumer_heiti = serializers.CharField(
        source='yfirlykilnumer.heiti',
        read_only=True,
        allow_null=True
    )
    stada = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Bokhaldslykill
        fields = [
            'id', 'lykilnumer', 'heiti', 'lysing', 'tegund',
            'yfirlykilnumer', 'yfirlykilnumer_heiti', 'er_virkur',
            'stada', 'stofnad', 'uppfaert'
        ]
        read_only_fields = ['stofnad', 'uppfaert']


class FaerslaSerializer(serializers.ModelSerializer):
    vidskiptavinur_nafn = serializers.CharField(
        source='vidskiptavinur.nafn',
        read_only=True,
        allow_null=True
    )
    starfsmadur_nafn = serializers.CharField(
        source='starfsmadur.notandi.fullt_nafn',
        read_only=True,
        allow_null=True
    )
    bokhaldslykill_heiti = serializers.CharField(
        source='bokhaldslykill.heiti',
        read_only=True
    )
    
    class Meta:
        model = Faersla
        fields = [
            'id', 'faerslunumer', 'dagsetning', 'lysing', 'bokhaldslykill',
            'bokhaldslykill_heiti', 'debet_fjarhaed', 'kredit_fjarhaed',
            'fjarhaed', 'tegund', 'flokkur',
            'vidskiptavinur', 'vidskiptavinur_nafn', 'starfsmadur',
            'starfsmadur_nafn', 'athugasemdir', 'skrad_af', 'stofnad'
        ]
        read_only_fields = ['faerslunumer', 'stofnad']


class SuperAdminKerfiskaukandiSerializer(serializers.ModelSerializer):
    sub_admin_notandi_nafn = serializers.CharField(
        source='sub_admin_notandi.fullt_nafn',
        read_only=True,
        allow_null=True
    )
    fullt_simanumer = serializers.CharField(read_only=True)
    
    class Meta:
        model = SuperAdminKerfiskaupandi
        fields = [
            'id', 'item_id', 'fyrirtaeki_nafn', 'kennitala', 'abyrgdarmaður',
            'netfang', 'heimilisfang', 'postnumer', 'sveitarfelag', 'land',
            'landsnumer', 'simanumer', 'fullt_simanumer', 'sub_admin_notandi',
            'sub_admin_notandi_nafn', 'er_virkur', 'athugasemdir',
            'stofnad', 'uppfaert'
        ]
        read_only_fields = ['item_id', 'landsnumer', 'fullt_simanumer', 'stofnad', 'uppfaert']


class MaelabordSerializer(serializers.ModelSerializer):
    notandi_nafn = serializers.CharField(
        source='notandi.fullt_nafn',
        read_only=True
    )
    
    class Meta:
        model = Maelabord
        fields = [
            'id', 'notandi', 'notandi_nafn', 'dagsetning',
            'fjoldi_maettra', 'fjoldi_verkefna_i_vinnslu',
            'fjoldi_verkefna_lokid', 'heildar_tekjur',
            'heildar_gjold', 'stofnad'
        ]
        read_only_fields = ['stofnad']
