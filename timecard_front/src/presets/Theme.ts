import { definePreset } from '@primeuix/themes';
import Aura from '@primeuix/themes/aura';
import { colors } from '@/config/colors';

const TheTheme = definePreset(Aura, {
    semantic: {
        primary: colors.primary,
        mygray: colors.mygray,
        colorScheme: {
            light: {
                primary: {
                    color: '{mygray.950}',
                    contrastColor: '#ffffff',
                    hoverColor: '{mygray.900}',
                    activeColor: '{mygray.800}'
                },
                highlight: {
                    background: '{mygray.950}',
                    focusBackground: '{mygray.700}',
                    color: '#ffffff',
                    focusColor: '#ffffff'
                },
            },
            dark: {
                primary: {
                    color: '{mygray.50}',
                    contrastColor: '{mygray.950}',
                    hoverColor: '{mygray.100}',
                    activeColor: '{mygray.200}'
                },
                highlight: {
                    background: '{mygray.50}',
                    focusBackground: '{mygray.300}',
                    color: '{mygray.950}',
                    focusColor: '{mygray.950}'
                }
            }
        }
    }
});

export default TheTheme;
