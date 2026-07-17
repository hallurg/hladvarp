(function () {
    function shouldShowSplash() {
        // Show once per browser tab session.
        if (sessionStorage.getItem('knSplashShown') === '1') {
            return false;
        }
        return true;
    }

    function showSplash() {
        var splash = document.getElementById('kn-splash');
        if (!splash) {
            return;
        }

        splash.classList.add('is-visible');
        document.body.classList.add('kn-splash-lock');

        setTimeout(function () {
            splash.classList.remove('is-visible');
            document.body.classList.remove('kn-splash-lock');
            sessionStorage.setItem('knSplashShown', '1');
        }, 3000);
    }

    document.addEventListener('DOMContentLoaded', function () {
        if (shouldShowSplash()) {
            showSplash();
        }
    });
})();
