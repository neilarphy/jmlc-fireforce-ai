// Утилита для управления цветовыми схемами
export function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

export function applyColorScheme(scheme) {
    let primary, secondary, accent, gradientStart, gradientEnd;

    switch (scheme) {
        case 'red':
            primary = '#dc2626';
            secondary = '#ef4444';
            accent = '#f97316';
            gradientStart = '#dc2626';
            gradientEnd = '#f97316';
            break;
        case 'green':
            primary = '#059669';
            secondary = '#10b981';
            accent = '#22c55e';
            gradientStart = '#059669';
            gradientEnd = '#22c55e';
            break;
        case 'orange':
            primary = '#ea580c';
            secondary = '#f97316';
            accent = '#f59e0b';
            gradientStart = '#ea580c';
            gradientEnd = '#f59e0b';
            break;
        case 'purple':
            primary = '#7c3aed';
            secondary = '#8b5cf6';
            accent = '#a855f7';
            gradientStart = '#7c3aed';
            gradientEnd = '#a855f7';
            break;
        default: // blue
            primary = '#2563eb';
            secondary = '#3b82f6';
            accent = '#6366f1';
            gradientStart = '#2563eb';
            gradientEnd = '#059669';
    }

    // Конвертируем цвета в RGB
    const primaryRgb = hexToRgb(primary);
    const secondaryRgb = hexToRgb(secondary);
    const accentRgb = hexToRgb(accent);

    // Устанавливаем CSS переменные для Quasar
    document.documentElement.style.setProperty('--q-primary', primary);
    document.documentElement.style.setProperty('--q-secondary', secondary);
    document.documentElement.style.setProperty('--q-accent', accent);

    // Устанавливаем кастомные CSS переменные для градиентов
    document.documentElement.style.setProperty('--app-gradient-start', gradientStart);
    document.documentElement.style.setProperty('--app-gradient-end', gradientEnd);
    document.documentElement.style.setProperty('--app-primary', primary);
    document.documentElement.style.setProperty('--app-secondary', secondary);
    document.documentElement.style.setProperty('--app-accent', accent);

    // Устанавливаем RGB переменные для использования в rgba()
    if (primaryRgb) {
        document.documentElement.style.setProperty('--app-primary-rgb', `${primaryRgb.r}, ${primaryRgb.g}, ${primaryRgb.b}`);
    }
    if (secondaryRgb) {
        document.documentElement.style.setProperty('--app-secondary-rgb', `${secondaryRgb.r}, ${secondaryRgb.g}, ${secondaryRgb.b}`);
    }
    if (accentRgb) {
        document.documentElement.style.setProperty('--app-accent-rgb', `${accentRgb.r}, ${accentRgb.g}, ${accentRgb.b}`);
    }

    // Обновляем градиенты на всех страницах
    updatePageGradients();
}

export function updatePageGradients() {
    // Добавляем глобальные стили для всех страниц
    let globalStyles = document.getElementById('app-color-scheme-styles');
    if (!globalStyles) {
        globalStyles = document.createElement('style');
        globalStyles.id = 'app-color-scheme-styles';
        document.head.appendChild(globalStyles);
    }

    globalStyles.textContent = `
        .page-header .text-h4 {
            background: linear-gradient(135deg, var(--app-gradient-start), var(--app-gradient-end)) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
        }
        
        .dashboard-card .card-header {
            background: linear-gradient(135deg, rgba(var(--app-primary-rgb), 0.1), rgba(var(--app-secondary-rgb), 0.1)) !important;
        }
        
        .settings-page, .dashboard-page, .map-page, .predictions-page, .history-page, .alerts-page, .analytics-page, .team-page {
            background: linear-gradient(135deg, rgba(var(--app-primary-rgb), 0.03) 0%, rgba(var(--app-secondary-rgb), 0.03) 100%) !important;
        }
        
        .setting-item:hover, .member-item:hover, .alert-item:hover, .region-item:hover, .weather-item:hover, .trend-item:hover {
            background: rgba(var(--app-primary-rgb), 0.05) !important;
            border-color: rgba(var(--app-primary-rgb), 0.1) !important;
        }
        
        .action-btn:hover, .add-member-btn:hover, .refresh-btn:hover, .save-btn:hover {
            background: rgba(var(--app-primary-rgb), 0.1) !important;
        }
        
        .report-btn:hover, .header-btn:hover {
            box-shadow: 0 4px 12px rgba(var(--app-primary-rgb), 0.3) !important;
        }
    `;
}

// Функция для инициализации цветовой схемы при загрузке приложения
export function initColorScheme() {
    const savedColorScheme = localStorage.getItem('colorScheme');
    if (savedColorScheme) {
        try {
            const scheme = JSON.parse(savedColorScheme);
            applyColorScheme(scheme.value);
        } catch (error) {
            console.error('Error parsing saved color scheme:', error);
            applyColorScheme('blue');
        }
    } else {
        applyColorScheme('blue');
    }
} 