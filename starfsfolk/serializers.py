from rest_framework import serializers
from .models import (
    Notandi, Starfsmadur, Maeting, Fridagur, 
    Vinnukostnadur, Serhaefi, TimaklukkuTaeki,
    TimaklukkuAtburdur, TimaklukkuLeidretting
)


class NotandiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notandi
        fields = [
            'id', 'notandanafn', 'email', 'fullt_nafn', 'simanumer',
            'notendategund', 'er_virkur', 'date_joined'
        ]
        read_only_fields = ['date_joined']


class SerhaefiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serhaefi
        fields = ['id', 'heiti', 'lysing', 'stofnad']
        read_only_fields = ['stofnad']


class StarfsmadurSerializer(serializers.ModelSerializer):
    notandi = NotandiSerializer(read_only=True)
    serhaefi = SerhaefiSerializer(many=True, read_only=True)
    
    class Meta:
        model = Starfsmadur
        fields = [
            'id', 'notandi', 'starfsmannanumer', 'kennitala', 
            'heimilisfang', 'simanumer', 'starfstitill', 'active_directory_notandi',
            'qr_kodi', 'aeskilegur_moettartimi', 'aeskilegur_brottfararstimi',
            'serhaefi', 'er_virkur', 'rodun', 'stofnad', 'uppfaert'
        ]
        read_only_fields = ['starfsmannanumer', 'qr_kodi', 'stofnad', 'uppfaert']


class StarfsmadurCreateSerializer(serializers.ModelSerializer):
    notandanafn = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    fullt_nafn = serializers.CharField(write_only=True)
    lykilord = serializers.CharField(write_only=True, style={'input_type': 'password'})
    serhaefi_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Starfsmadur
        fields = [
            'notandanafn', 'email', 'fullt_nafn', 'lykilord',
            'kennitala', 'heimilisfang', 'simanumer', 'starfstitill',
            'active_directory_notandi', 'aeskilegur_moettartimi', 
            'aeskilegur_brottfararstimi', 'rodun', 'serhaefi_ids'
        ]
    
    def create(self, validated_data):
        # Fjarlægja notendagögn
        notandanafn = validated_data.pop('notandanafn')
        email = validated_data.pop('email')
        fullt_nafn = validated_data.pop('fullt_nafn')
        lykilord = validated_data.pop('lykilord')
        serhaefi_ids = validated_data.pop('serhaefi_ids', [])
        
        # Búa til notanda
        notandi = Notandi.objects.create_user(
            notandanafn=notandanafn,
            email=email,
            fullt_nafn=fullt_nafn,
            lykilord=lykilord,
            notendategund='STARFSMADUR',
            er_starfsmadur=True
        )
        
        # Búa til starfsmann
        starfsmadur = Starfsmadur.objects.create(
            notandi=notandi,
            **validated_data
        )
        
        # Bæta við sérhæfi
        if serhaefi_ids:
            starfsmadur.serhaefi.set(serhaefi_ids)
        
        return starfsmadur


class MaetingSerializer(serializers.ModelSerializer):
    starfsmadur_nafn = serializers.CharField(
        source='starfsmadur.notandi.fullt_nafn', 
        read_only=True
    )
    
    class Meta:
        model = Maeting
        fields = [
            'id', 'starfsmadur', 'starfsmadur_nafn', 'dagsetning',
            'moettartimi', 'brottfararstimi', 'status', 'athugasemdir', 'stofnad'
        ]
        read_only_fields = ['stofnad']


class TimaklukkuTaekiSerializer(serializers.ModelSerializer):
    starfsmadur_nafn = serializers.CharField(
        source='starfsmadur.notandi.fullt_nafn',
        read_only=True
    )

    class Meta:
        model = TimaklukkuTaeki
        fields = [
            'id', 'starfsmadur', 'starfsmadur_nafn', 'device_label',
            'status', 'last_seen', 'created_at', 'revoked_at'
        ]
        read_only_fields = [
            'starfsmadur', 'status', 'last_seen', 'created_at', 'revoked_at'
        ]


class TimaklukkuAtburdurSerializer(serializers.ModelSerializer):
    starfsmadur_nafn = serializers.CharField(
        source='starfsmadur.notandi.fullt_nafn',
        read_only=True
    )
    taeki_label = serializers.CharField(source='taeki.device_label', read_only=True)

    class Meta:
        model = TimaklukkuAtburdur
        fields = [
            'id', 'starfsmadur', 'starfsmadur_nafn', 'taeki', 'taeki_label',
            'event_type', 'timestamp', 'source', 'client_event_id', 'note',
            'created_by'
        ]
        read_only_fields = fields


class TimaklukkuLeidrettingSerializer(serializers.ModelSerializer):
    starfsmadur_nafn = serializers.CharField(
        source='starfsmadur.notandi.fullt_nafn',
        read_only=True
    )
    reviewed_by_nafn = serializers.CharField(
        source='reviewed_by.fullt_nafn',
        read_only=True
    )

    class Meta:
        model = TimaklukkuLeidretting
        fields = [
            'id', 'starfsmadur', 'starfsmadur_nafn', 'maeting',
            'requested_change', 'reason', 'status', 'reviewed_by',
            'reviewed_by_nafn', 'reviewed_at', 'manager_note',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'starfsmadur', 'status', 'reviewed_by', 'reviewed_by_nafn',
            'reviewed_at', 'manager_note', 'created_at', 'updated_at'
        ]


class FridagurSerializer(serializers.ModelSerializer):
    starfsmadur_nafn = serializers.CharField(
        source='starfsmadur.notandi.fullt_nafn', 
        read_only=True
    )
    samthykkt_af_nafn = serializers.CharField(
        source='samthykkt_af.fullt_nafn', 
        read_only=True
    )
    
    class Meta:
        model = Fridagur
        fields = [
            'id', 'starfsmadur', 'starfsmadur_nafn', 'fra_dagsetning',
            'til_dagsetning', 'fridags_tegund', 'lysing', 'stada',
            'samthykkt_af', 'samthykkt_af_nafn', 'stofnad', 'uppfaert'
        ]
        read_only_fields = ['samthykkt_af', 'stofnad', 'uppfaert']


class VinnukostnadurSerializer(serializers.ModelSerializer):
    starfsmadur_nafn = serializers.CharField(
        source='starfsmadur.notandi.fullt_nafn', 
        read_only=True
    )
    
    class Meta:
        model = Vinnukostnadur
        fields = [
            'id', 'starfsmadur', 'starfsmadur_nafn', 'dagsetning',
            'fjarhaed', 'kostnadar_tegund', 'lysing', 'er_greitt', 'stofnad'
        ]
        read_only_fields = ['stofnad']
