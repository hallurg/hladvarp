from rest_framework import serializers
from .models import (
    Verkbeiðni, Verkefni, VerkefniSkra,
    VerkefniAthugasemd, DeadlineAminnning
)


class VerkbeidniSerializer(serializers.ModelSerializer):
    vidskiptavinur_nafn = serializers.CharField(
        source='vidskiptavinur.nafn',
        read_only=True
    )
    stofnad_af_nafn = serializers.CharField(
        source='stofnad_af.fullt_nafn',
        read_only=True
    )
    
    class Meta:
        model = Verkbeiðni
        fields = [
            'id', 'vidskiptavinur', 'vidskiptavinur_nafn', 'titill',
            'lysing', 'forgangur', 'stada', 'stofnad_af', 'stofnad_af_nafn',
            'samthykkt_af', 'stofnad', 'uppfaert'
        ]
        read_only_fields = ['stofnad', 'uppfaert']


class VerkefniSkraSerializer(serializers.ModelSerializer):
    upphlad_af_nafn = serializers.CharField(
        source='upphlad_af.fullt_nafn',
        read_only=True
    )
    
    class Meta:
        model = VerkefniSkra
        fields = [
            'id', 'verkefni', 'skra', 'tegund', 'lysing',
            'upphlad_af', 'upphlad_af_nafn', 'upphlad'
        ]
        read_only_fields = ['upphlad']


class VerkefniAthugasemdSerializer(serializers.ModelSerializer):
    notandi_nafn = serializers.CharField(
        source='notandi.fullt_nafn',
        read_only=True
    )
    
    class Meta:
        model = VerkefniAthugasemd
        fields = [
            'id', 'verkefni', 'notandi', 'notandi_nafn',
            'athugasemd', 'stofnad'
        ]
        read_only_fields = ['stofnad']


class VerkefniSerializer(serializers.ModelSerializer):
    starfsmadur_nafn = serializers.CharField(
        source='starfsmadur.notandi.fullt_nafn',
        read_only=True
    )
    verkbeidni_titill = serializers.CharField(
        source='verkbeidni.titill',
        read_only=True
    )
    progress_percent = serializers.IntegerField(read_only=True)
    skrar = VerkefniSkraSerializer(many=True, read_only=True)
    athugasemdir = VerkefniAthugasemdSerializer(many=True, read_only=True)
    
    class Meta:
        model = Verkefni
        fields = [
            'id', 'verkbeidni', 'verkbeidni_titill', 'starfsmadur',
            'starfsmadur_nafn', 'titill', 'lysing', 'stada',
            'vinnustadur', 'deadline', 'rodun', 'uthlutad_af', 'progress_percent',
            'skrar', 'athugasemdir', 'stofnad', 'uppfaert', 'lokad'
        ]
        read_only_fields = ['stofnad', 'uppfaert']


class VerkefniListSerializer(serializers.ModelSerializer):
    """Einfaldari serializer fyrir lista"""
    starfsmadur_nafn = serializers.CharField(
        source='starfsmadur.notandi.fullt_nafn',
        read_only=True
    )
    progress_percent = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Verkefni
        fields = [
            'id', 'titill', 'starfsmadur', 'starfsmadur_nafn',
            'stada', 'vinnustadur', 'deadline', 'rodun', 'progress_percent', 'stofnad'
        ]


class DeadlineAminnningSerializer(serializers.ModelSerializer):
    verkefni_titill = serializers.CharField(
        source='verkefni.titill',
        read_only=True
    )
    
    class Meta:
        model = DeadlineAminnning
        fields = [
            'id', 'verkefni', 'verkefni_titill', 'aminntar_dagar_fyrir',
            'send_aminningu', 'aminningu_send', 'stofnad'
        ]
        read_only_fields = ['aminningu_send', 'stofnad']
