import math

def calculate_pmv_ppd(clo, met, wme, ta, tr, vel, rh, pa):
    def fnps(ta):
        return math.exp(16.6536 - 4030.183 / (ta + 235))

    if pa == 0:
        pa = rh * 10 * fnps(ta)
    
    icl = 0.155 * clo
    m = met * 58.15
    w = wme * 58.15
    mw = m - w
    
    if icl < 0.078:
        fcl = 1 + 1.29 * icl
    else:
        fcl = 1.05 + 0.645 * icl
    
    hcf = 12.1 * math.sqrt(vel)
    taa = ta + 273
    tra = tr + 273
    
    tcla = taa + (35.5 - ta) / (3.5 * (6.45 * icl + 0.1))
    
    p1 = icl * fcl
    p2 = p1 * 3.96
    p3 = p1 * 100
    p4 = p1 * taa
    p5 = 308.7 - 0.028 * mw + p2 * math.pow(tra / 100, 4)
    
    xn = tcla / 100
    xf = xn
    eps = 0.00015
    n = 0
    
    while True:
        xf = (xf + xn) / 2
        hcn = 2.38 * abs(100 * xf - taa) ** 0.25
        hc = max(hcf, hcn)
        xn = (p5 + p4 * hc - p2 * math.pow(xf, 4)) / (100 + p3 * hc)
        n += 1
        if n > 150 or abs(xn - xf) <= eps:
            break
    
    tcl = 100 * xn - 273
    
    hl1 = 3.05 * 0.001 * (5733 - 6.99 * mw - pa)
    hl2 = 0
    if mw > 58.15:
        hl2 = 0.42 * (mw - 58.15)
    hl3 = 1.7 * 0.00001 * m * (5867 - pa)
    hl4 = 0.0014 * m * (34 - ta)
    hl5 = 3.96 * fcl * (math.pow(xn, 4) - math.pow(tra / 100, 4))
    hl6 = fcl * hc * (tcl - ta)
    
    ts = 0.303 * math.exp(-0.036 * m) + 0.028
    pmv = ts * (mw - hl1 - hl2 - hl3 - hl4 - hl5 - hl6)
    ppd = 100 - 95 * math.exp(-0.03353 * pmv ** 4 - 0.2179 * pmv ** 2)
    
    return pmv, ppd

# Parameters
wme = 0.0
pa = 0.0

# Initialize variables
clothingLevel = 0.5
metabolicRate = 1.2
airTemperature = 21
radiantTemperature = 25
airVelocity = 0.2
relativeHumidity = 60

vsg = airVelocity
#vsg = airVelocity + 0.3 * (metabolicRate - 1)

pmv, ppd = calculate_pmv_ppd(clo=clothingLevel, met=metabolicRate, wme=wme, ta=airTemperature, tr=radiantTemperature, vel=vsg, rh=relativeHumidity, pa=pa)
print("pmv: {} | ppd: {}".format(pmv, ppd))