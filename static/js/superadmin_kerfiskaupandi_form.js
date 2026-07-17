(function () {
    function digitsOnly(value) {
        return (value || '').replace(/\D/g, '');
    }

    var postnumerMap = {
        '101': 'Reykjavik', '102': 'Reykjavik', '103': 'Reykjavik', '104': 'Reykjavik',
        '105': 'Reykjavik', '107': 'Reykjavik', '108': 'Reykjavik', '109': 'Reykjavik',
        '110': 'Reykjavik', '111': 'Reykjavik', '112': 'Reykjavik', '113': 'Reykjavik',
        '116': 'Reykjavik', '170': 'Seltjarnarnes', '190': 'Vogar', '200': 'Kopavogur',
        '201': 'Kopavogur', '203': 'Kopavogur', '210': 'Gardabaer', '220': 'Hafnarfjordur',
        '221': 'Hafnarfjordur', '225': 'Gardabaer', '230': 'Reykjanesbaer', '232': 'Reykjanesbaer',
        '233': 'Reykjanesbaer', '240': 'Grindavik', '245': 'Sandgerdi', '250': 'Gardur',
        '260': 'Reykjanesbaer', '270': 'Mosfellsbaer', '300': 'Akranes', '310': 'Borgarnes',
        '320': 'Reykholt', '340': 'Stykkisholmur', '400': 'Isafjordur', '500': 'Stadarskali',
        '550': 'Saudarkrokur', '600': 'Akureyri', '603': 'Akureyri', '610': 'Grenivik',
        '640': 'Husavik', '700': 'Egilsstadir', '710': 'Seydisfjordur', '730': 'Reydarfjordur',
        '735': 'Eskifjordur', '740': 'Neskaupstadur', '750': 'Faskrudsfjordur', '760': 'Breiddalsvik',
        '780': 'Hofn', '800': 'Selfoss', '810': 'Hveragerdi', '815': 'Thorlakshofn',
        '820': 'Eyrarbakki', '825': 'Stokkseyri', '840': 'Laugarvatn', '850': 'Hella',
        '860': 'Hvolsvollur', '870': 'Vik', '900': 'Vestmannaeyjar'
    };

    var phoneRules = {
        'Island': { code: '+354', min: 7, max: 7 },
        'Danmork': { code: '+45', min: 8, max: 8 },
        'Noregur': { code: '+47', min: 8, max: 8 },
        'Sviþjod': { code: '+46', min: 7, max: 13 },
        'Finnland': { code: '+358', min: 7, max: 12 },
        'Bandarikin': { code: '+1', min: 10, max: 10 },
        'Kanada': { code: '+1', min: 10, max: 10 },
        'Bretland': { code: '+44', min: 9, max: 10 },
        'Thyskaland': { code: '+49', min: 7, max: 13 },
        'Frakkland': { code: '+33', min: 9, max: 9 },
        'Spann': { code: '+34', min: 9, max: 9 },
        'Poland': { code: '+48', min: 9, max: 9 }
    };

    function updateKennitalaInput(kennitalaInput) {
        var digits = digitsOnly(kennitalaInput.value).slice(0, 10);
        if (digits.length > 6) {
            kennitalaInput.value = digits.slice(0, 6) + '-' + digits.slice(6);
        } else {
            kennitalaInput.value = digits;
        }
    }

    function updateSveitarfelag(postnumerInput, sveitarfelagInput, landInput) {
        var postnumer = digitsOnly(postnumerInput.value).slice(0, 3);
        postnumerInput.value = postnumer;
        if (landInput && landInput.value !== 'Island') {
            if (!sveitarfelagInput.value) {
                sveitarfelagInput.value = '';
            }
            return;
        }
        var sveitarfelag = postnumerMap[postnumer];
        if (sveitarfelag) {
            sveitarfelagInput.value = sveitarfelag;
        }
    }

    function updatePhoneRule(landInput, landsnumerInput, simanumerInput) {
        var land = landInput.value;
        var rule = phoneRules[land];
        if (!rule) {
            return;
        }

        landsnumerInput.value = rule.code;
        simanumerInput.maxLength = rule.max;
        simanumerInput.placeholder = 'Lengd: ' + rule.min + '-' + rule.max + ' tolustafir';

        var digits = digitsOnly(simanumerInput.value);
        if (digits.length > rule.max) {
            simanumerInput.value = digits.slice(0, rule.max);
        } else {
            simanumerInput.value = digits;
        }

        if (digits.length < rule.min || digits.length > rule.max) {
            simanumerInput.setCustomValidity(
                'Simanumer fyrir ' + land + ' þarf ad vera ' + rule.min + '-' + rule.max + ' tolustafir.'
            );
        } else {
            simanumerInput.setCustomValidity('');
        }

        var help = document.getElementById('simanumer-country-prefix-help');
        if (!help) {
            help = document.createElement('div');
            help.id = 'simanumer-country-prefix-help';
            help.style.marginTop = '4px';
            help.style.fontSize = '12px';
            simanumerInput.parentElement.appendChild(help);
        }
        help.textContent = 'Landsnumer: ' + rule.code;
    }

    document.addEventListener('DOMContentLoaded', function () {
        var kennitalaInput = document.getElementById('id_kennitala');
        var postnumerInput = document.getElementById('id_postnumer');
        var sveitarfelagInput = document.getElementById('id_sveitarfelag');
        var landInput = document.getElementById('id_land');
        var landsnumerInput = document.getElementById('id_landsnumer');
        var simanumerInput = document.getElementById('id_simanumer');

        if (kennitalaInput) {
            kennitalaInput.addEventListener('input', function () {
                updateKennitalaInput(kennitalaInput);
            });
            updateKennitalaInput(kennitalaInput);
        }

        if (postnumerInput && sveitarfelagInput) {
            postnumerInput.addEventListener('input', function () {
                updateSveitarfelag(postnumerInput, sveitarfelagInput, landInput);
            });
            updateSveitarfelag(postnumerInput, sveitarfelagInput, landInput);
        }

        if (landInput && landsnumerInput && simanumerInput) {
            landInput.addEventListener('change', function () {
                updatePhoneRule(landInput, landsnumerInput, simanumerInput);
                if (postnumerInput && sveitarfelagInput) {
                    updateSveitarfelag(postnumerInput, sveitarfelagInput, landInput);
                }
            });
            simanumerInput.addEventListener('input', function () {
                var digits = digitsOnly(simanumerInput.value);
                simanumerInput.value = digits;
                updatePhoneRule(landInput, landsnumerInput, simanumerInput);
            });
            updatePhoneRule(landInput, landsnumerInput, simanumerInput);
        }
    });
})();
