(function (global) {
    function showNotification(message, type) {
        var el = document.getElementById('toast-notification');
        if (!el) {
            el = document.createElement('div');
            el.id = 'toast-notification';
            el.className = 'toast-notification';
            document.body.appendChild(el);
        }
        var colors = { success: 'var(--toast-ok)', error: 'var(--toast-err)', info: 'var(--toast-info)' };
        el.style.background = colors[type] || colors.info;
        el.textContent = message;
        el.style.display = 'block';
        el.setAttribute('data-show', '1');
        clearTimeout(global._toastTimer);
        global._toastTimer = setTimeout(function () {
            el.removeAttribute('data-show');
            el.style.display = 'none';
        }, 3800);
    }
    global.showNotification = showNotification;

    function initLearnShellDrawers() {
        var body = document.body;
        if (!body.classList.contains('page-learn')) return;

        var backdrop = document.getElementById('learnNavBackdrop');
        var left = document.getElementById('learnSidebarLeft');
        var right = document.getElementById('learnSidebarRight');
        var openLeft = document.getElementById('learnOpenLeft');
        var openRight = document.getElementById('learnOpenRight');
        var closeLeft = document.getElementById('learnCloseLeft');
        var closeRight = document.getElementById('learnCloseRight');

        if (!backdrop || !left || !right) return;

        var lastFocus = null;

        function isDrawerLayout() {
            return global.matchMedia && global.matchMedia('(max-width: 900px)').matches;
        }

        function setBackdrop(on) {
            if (on) {
                backdrop.classList.add('is-visible');
                backdrop.setAttribute('aria-hidden', 'false');
            } else {
                backdrop.classList.remove('is-visible');
                backdrop.setAttribute('aria-hidden', 'true');
            }
        }

        function closeAll() {
            left.classList.remove('learn-sidebar--open');
            right.classList.remove('learn-sidebar--open');
            setBackdrop(false);
            body.classList.remove('learn-drawer-open');
            if (openLeft) openLeft.setAttribute('aria-expanded', 'false');
            if (openRight) openRight.setAttribute('aria-expanded', 'false');
            if (lastFocus && typeof lastFocus.focus === 'function') {
                try {
                    lastFocus.focus();
                } catch (e) {}
                lastFocus = null;
            }
        }

        function openSide(which) {
            if (!isDrawerLayout()) return;
            lastFocus = document.activeElement;
            if (which === 'left') {
                left.classList.add('learn-sidebar--open');
                right.classList.remove('learn-sidebar--open');
                if (openLeft) openLeft.setAttribute('aria-expanded', 'true');
                if (openRight) openRight.setAttribute('aria-expanded', 'false');
            } else {
                right.classList.add('learn-sidebar--open');
                left.classList.remove('learn-sidebar--open');
                if (openRight) openRight.setAttribute('aria-expanded', 'true');
                if (openLeft) openLeft.setAttribute('aria-expanded', 'false');
            }
            setBackdrop(true);
            body.classList.add('learn-drawer-open');
        }

        function onOpenLeft(e) {
            e.preventDefault();
            if (!isDrawerLayout()) return;
            if (left.classList.contains('learn-sidebar--open')) closeAll();
            else openSide('left');
        }

        function onOpenRight(e) {
            e.preventDefault();
            if (!isDrawerLayout()) return;
            if (right.classList.contains('learn-sidebar--open')) closeAll();
            else openSide('right');
        }

        if (openLeft) openLeft.addEventListener('click', onOpenLeft);
        if (openRight) openRight.addEventListener('click', onOpenRight);
        if (closeLeft) closeLeft.addEventListener('click', closeAll);
        if (closeRight) closeRight.addEventListener('click', closeAll);
        backdrop.addEventListener('click', closeAll);

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && body.classList.contains('learn-drawer-open')) {
                closeAll();
            }
        });

        left.addEventListener('click', function (e) {
            if (!isDrawerLayout()) return;
            var t = e.target;
            if (t && t.closest && t.closest('a[href]')) closeAll();
        });

        right.addEventListener('click', function (e) {
            if (!isDrawerLayout()) return;
            var t = e.target;
            if (t && t.closest && t.closest('a[href], .module-row[role="button"]')) closeAll();
        });

        global.addEventListener(
            'resize',
            function () {
                if (!isDrawerLayout()) closeAll();
            },
            { passive: true }
        );
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initLearnShellDrawers);
    } else {
        initLearnShellDrawers();
    }
})(window);
