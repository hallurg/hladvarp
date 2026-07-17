from rest_framework import serializers
from .models import FasturLidur, Reikningur, ReikningsLidur, Greidsla


class FasturLidurSerializer(serializers.ModelSerializer):
    class Meta:
        model = FasturLidur
        fields = [
            'id', 'heiti', 'lysing', 'fjarhaed', 'er_virkur',
            'stofnad', 'uppfaert'
        ]
        read_only_fields = ['stofnad', 'uppfaert']


class ReikningsLidurSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReikningsLidur
        fields = [
            'id', 'reikningur', 'lysing', 'magn', 'einingarverð',
            'heildarfjarhaed', 'tegund', 'stofnad'
        ]
        read_only_fields = ['heildarfjarhaed', 'stofnad']


class GreidslaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Greidsla
        fields = [
            'id', 'reikningur', 'fjarhaed', 'greidsludagsetning',
            'greidslu_adferd', 'athugasemdir', 'skrad_af', 'stofnad'
        ]
        read_only_fields = ['stofnad']


class ReikningurSerializer(serializers.ModelSerializer):
    vidskiptavinur_nafn = serializers.CharField(
        source='vidskiptavinur.nafn',
        read_only=True
    )
    lidur = ReikningsLidurSerializer(many=True, read_only=True)
    greidslur = GreidslaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Reikningur
        fields = [
            'id', 'vidskiptavinur', 'vidskiptavinur_nafn', 'reikningsnumer',
            'verkefni', 'reikningsdagsetning', 'gjalddagi', 'eindagi',
            'heildarfjarhaed', 'vsk_fjarhaed', 'stada', 'er_greiddur',
            'athugasemdir', 'lidur', 'greidslur', 'stofnad_af',
            'stofnad', 'uppfaert'
        ]
        read_only_fields = ['reikningsnumer', 'stofnad', 'uppfaert']


class ReikningurListSerializer(serializers.ModelSerializer):
    """Einfaldari serializer fyrir lista"""
    vidskiptavinur_nafn = serializers.CharField(
        source='vidskiptavinur.nafn',
        read_only=True
    )
    
    class Meta:
        model = Reikningur
        fields = [
            'id', 'reikningsnumer', 'vidskiptavinur', 'vidskiptavinur_nafn',
            'reikningsdagsetning', 'gjalddagi', 'heildarfjarhaed',
            'stada', 'er_greiddur'
        ]
