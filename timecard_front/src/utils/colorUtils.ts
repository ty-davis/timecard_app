export const secondaryColor = (color: string, darkModeMin: number = 0.25, lightModeMin: number = 0.85) => {
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const isDarkMode = darkModeQuery.matches;
    // converting to hsl
    const r = parseInt(color.slice(1, 3), 16) / 255;
    const g = parseInt(color.slice(3, 5), 16) / 255;
    const b = parseInt(color.slice(5), 16) / 255;

    const minVal = Math.min(r, g, b);
    const maxVal = Math.max(r, g, b);
    let bottom = maxVal - minVal;
    if (bottom === 0) {
        bottom = 0.0000001;
    }


    let h = 0;
    if (maxVal === r) {
      h = (g - b) / (bottom);        
    } else if (maxVal === g) {
      h = 2.0 + (b - r) / (bottom);
    } else {
      h = 4.0 + (r - g) / (bottom);
    }
    h *= 60;
    

    let l = (maxVal + minVal) / 2;

    let s = 0;
    if (maxVal - minVal !== 0) {
      s = (maxVal - minVal) / (1 - Math.abs(2 * l - 1));
    }

    // check the lightness against the theme
    if (isDarkMode) {
      l = Math.min(l, darkModeMin);
    } else {
      l = Math.max(l, lightModeMin);
    }

    // back to rgb
    let c = (1 - Math.abs(2 * l - 1)) * s;
    let x = c * (1 - Math.abs((h / 60) % 2 - 1));
    let m = l - c/2;
    let rp = 0;
    let gp = 0;
    let bp = 0;
    if (h < 60)       { rp = c, gp = x, bp = 0 }
    else if (h < 120) { rp = x, gp = c, bp = 0 }
    else if (h < 180) { rp = 0, gp = c, bp = x }
    else if (h < 240) { rp = 0, gp = x, bp = c }
    else if (h < 300) { rp = x, gp = 0, bp = c }
    else              { rp = c, gp = 0, bp = x }

    const rpp = Math.round((rp+m)*255);
    const gpp = Math.round((gp+m)*255);
    const bpp = Math.round((bp+m)*255);
    return `#${rpp.toString(16).padStart(2, '0')}${gpp.toString(16).padStart(2, '0')}${bpp.toString(16).padStart(2, '0')}`;
};
