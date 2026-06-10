// Cumulus Cloud v8 — Dalí Clock (chrome rim + Roman numerals + asymmetric right-droop)
// Reference: silver pocket watch, right side droops, chrome metallic rim with highlights

uniform float uTime;
uniform float uBeat;

layout(location = 0) out vec4 fragColor;

// ── Noise ────────────────────────────────────────────────────────────

float hh(float n){ return fract(sin(n)*43758.5453); }
float n3(vec3 x){
    vec3 p=floor(x), f=fract(x); f=f*f*(3.0-2.0*f);
    float n=p.x+p.y*57.0+113.0*p.z;
    return mix(mix(mix(hh(n),hh(n+1.0),f.x),mix(hh(n+57.0),hh(n+58.0),f.x),f.y),
               mix(mix(hh(n+113.0),hh(n+114.0),f.x),mix(hh(n+170.0),hh(n+171.0),f.x),f.y),f.z);
}
const mat3 M=mat3(0.00,0.80,0.60,-0.80,0.36,-0.48,-0.60,-0.48,0.64);
float fbm5(vec3 p){float v=0.,a=.5;p+=vec3(31.4,27.2,14.1);for(int i=0;i<5;i++){v+=a*n3(p);p=M*p*2.;a*=.5;}return v*1.032;}
float fbm4(vec3 p){float v=0.,a=.5;p+=vec3(17.3,42.1,8.09);for(int i=0;i<4;i++){v+=a*n3(p);p=M*p*2.;a*=.5;}return v*1.067;}
float fbm3(vec3 p){float v=0.,a=.5;p+=vec3(5.77,93.1,55.6);for(int i=0;i<3;i++){v+=a*n3(p);p=M*p*2.;a*=.5;}return v*1.143;}

// ── Cloud density (v6, unchanged) ────────────────────────────────────

float layerDen(vec3 pos, float yBase, vec3 seed, float ct, float zOff){
    float yL=pos.y-yBase;
    float yEnv=smoothstep(-0.05,0.12,yL)*(1.-smoothstep(1.0,1.4,yL));
    if(yEnv<.001)return 0.;
    float xFall=1.-smoothstep(3.5,6.0,abs(pos.x));
    float zFall=1.-smoothstep(2.0,4.5,abs(pos.z-zOff));
    if(xFall*zFall<.001)return 0.;
    vec3 ds=vec3(ct*.60,ct*.14,ct*.35);
    float shape=fbm4(pos*.85+seed+ds);
    float detail=fbm5(pos*2.1+seed*.44+vec3(-ct*1.15,ct*.90,ct*1.50))*.21;
    float fine=n3(pos*4.6+seed*.28+vec3(ct*3.,ct*1.6,ct*2.3))*.10;
    float excess=max(0.,shape+detail+fine-0.55);
    return min(excess*45.,6.)*yEnv*xFall*zFall;
}
float shadowDen(vec3 pos){
    float yEnv=smoothstep(-.3,.2,pos.y)*(1.-smoothstep(4.2,5.,pos.y));
    if(yEnv<.001)return 0.;
    float e=max(0.,fbm3(pos*.85+vec3(uTime*.60,uTime*.14,uTime*.35))-0.52);
    return min(e*35.,5.)*yEnv;
}
const vec3 SUN=vec3(0.4497,0.8797,0.1499);
float shadowMarch(vec3 p){
    float acc=0.,s=.09;
    for(int i=0;i<5;i++){p+=SUN*s;acc+=shadowDen(p)*s;s*=1.7;}
    return exp(-acc*9.);
}
float cloudDen(vec3 pos){
    float ct=uTime;
    return layerDen(pos,0.10,vec3(0.),ct,-0.5)
          +layerDen(pos,1.50,vec3(19.3,11.7,7.3),ct*1.22,2.0)
          +layerDen(pos,2.85,vec3(38.6,24.1,15.5),ct*1.45,5.0);
}

// ── Dalí Clock ───────────────────────────────────────────────────────

const vec3  CLK_C = vec3(0.0, 1.95, 2.0);
const float CLK_R = 0.70;

float seg2(vec2 p, vec2 a, vec2 b){
    vec2 pa=p-a, ba=b-a;
    return length(pa - ba*clamp(dot(pa,ba)/dot(ba,ba), 0., 1.));
}

// Roman numeral primitives in glyph space (height ±1, width ±0.45)
float gI(vec2 p)          { return seg2(p, vec2(0.,-1.), vec2(0.,1.)); }
float gV(vec2 p)          { return min(seg2(p,vec2(-0.42,1.),vec2(0.,-1.)),
                                       seg2(p,vec2( 0.42,1.),vec2(0.,-1.))); }
float gX(vec2 p)          { return min(seg2(p,vec2(-0.42,1.),vec2(0.42,-1.)),
                                       seg2(p,vec2( 0.42,1.),vec2(-0.42,-1.))); }

// Returns signed distance to numeral n, in glyph space
// Caller scales: q = (uv - nPos) * 7.5
float glyph(vec2 q, int n){
    float d;
    if      (n==1)  d=gI(q);
    else if (n==2)  d=min(gI(q-vec2(-0.30,0.)),  gI(q-vec2(0.30,0.)));
    else if (n==3)  d=min(min(gI(q-vec2(-0.56,0.)), gI(q)), gI(q-vec2(0.56,0.)));
    else if (n==4)  d=min(gI(q-vec2(-0.46,0.)),  gV(q-vec2(0.20,0.)));
    else if (n==5)  d=gV(q);
    else if (n==6)  d=min(gV(q-vec2(-0.30,0.)),  gI(q-vec2(0.56,0.)));
    else if (n==7)  d=min(gV(q-vec2(-0.44,0.)),
                          min(gI(q-vec2(0.16,0.)),  gI(q-vec2(0.54,0.))));
    else if (n==8)  d=min(gV(q-vec2(-0.60,0.)),
                          min(gI(q-vec2(0.10,0.)),
                          min(gI(q-vec2(0.38,0.)),  gI(q-vec2(0.66,0.)))));
    else if (n==9)  d=min(gI(q-vec2(-0.54,0.)),  gX(q-vec2(0.18,0.)));
    else if (n==10) d=gX(q);
    else if (n==11) d=min(gX(q-vec2(-0.32,0.)),  gI(q-vec2(0.56,0.)));
    else            d=min(gX(q-vec2(-0.44,0.)),
                          min(gI(q-vec2(0.26,0.)),  gI(q-vec2(0.62,0.))));
    return d - 0.24; // stroke half-width
}

// Unmelt: maps displayed screen position back to original clock face UV
// RIGHT side droops down (matching reference image)
vec2 unmelt(vec2 q){
    // melt factor: 0 on left, 1 on right
    float mx  = smoothstep(-0.12, 0.82, q.x);
    // droop: only below y = -0.03
    float dy  = max(0.0, -(q.y + 0.03));
    // inverse: pull drooped positions back up
    q.y += dy * dy * mx * 2.0;
    // slight inward x-taper on melted part
    q.x -= dy * mx * 0.14;
    return q;
}

vec4 daliClock(vec2 q, vec3 rd){
    vec2  uv  = unmelt(q) / CLK_R;
    float r   = length(uv);
    if(r > 1.32) return vec4(0.0);

    // ── Constants ────────────────────────────────────────────────────
    float RIM_IN  = 0.90;
    float RIM_OUT = 1.18;
    float RIM_MID = 1.04;
    float RIM_H   = 0.14;

    // ── Masks ────────────────────────────────────────────────────────
    float faceM  = smoothstep(1.03, 0.93, r);
    float rimM   = smoothstep(RIM_OUT+0.03, RIM_OUT-0.02, r) *
                   smoothstep(RIM_IN -0.03, RIM_IN +0.02, r);
    // Crown knob (small circle at 12 o'clock, just above rim)
    float crownD = length(uv - vec2(0.0, 1.26)) - 0.088;
    float crownM = smoothstep(0.012, -0.012, crownD);

    // ── Chrome rim: rounded cross-section normal ──────────────────────
    // The rim cross-section is circular: normal curves from face-forward
    // (at inner edge) to radially-outward (at outer edge)
    float rimT   = clamp((r - RIM_MID) / RIM_H, -1.0, 1.0);
    float rimDep = sqrt(max(0.0, 1.0 - rimT * rimT));
    vec2  rimDir = (r > 0.001) ? normalize(uv) : vec2(0.0, 1.0);
    // Normal in 3D: radial in XY plane, -Z toward camera
    vec3  rimN   = normalize(vec3(rimDir * rimT, -rimDep));

    // Blinn-Phong for chrome (high shininess, cold silver color)
    vec3  V      = normalize(-rd);
    vec3  H      = normalize(V + SUN);
    float NdotH  = max(0.0, dot(rimN, H));
    float NdotL  = max(0.0, dot(rimN, SUN));
    float NdotV  = max(0.0, dot(rimN, V));
    float spec1  = pow(NdotH, 120.0) * 3.5;   // tight chrome glint
    float spec2  = pow(NdotH, 16.0)  * 0.60;  // wide silvery reflection
    // Schlick Fresnel (chrome: high F0 ≈ 0.95)
    float fres   = 0.95 + 0.05 * pow(1.0 - NdotV, 5.0);
    float specF  = (spec1 + spec2) * fres;

    vec3 rimBase = vec3(0.82, 0.86, 0.92);
    vec3 rimCol  = rimBase * (0.12 + NdotL * 0.72)
                 + vec3(1.12, 1.10, 1.06) * specF
                 + vec3(0.10, 0.12, 0.20) * pow(1.0-NdotV, 3.0); // cool rim fill

    // Crown: same chrome, separate normal
    vec2  crownOff  = uv - vec2(0.0, 1.26);
    float crownLen  = length(crownOff);
    vec3  crownN    = normalize(vec3(crownOff/(crownLen+0.001), -0.45));
    float cNdotH    = max(0.0, dot(crownN, H));
    vec3  crownCol  = rimBase*0.55 + vec3(1.0)*pow(cNdotH,90.0)*2.5;

    // ── Clock face ────────────────────────────────────────────────────
    // Cream/ivory, slight AO near rim junction, subtle center shadow
    float faceAO  = smoothstep(RIM_IN, RIM_IN-0.16, r);
    float faceDip = 1.0 - 0.06 * (1.0 - smoothstep(0.0, 0.55, r));
    vec3  faceCol = vec3(0.978, 0.968, 0.945) * (0.84 + 0.16*faceAO) * faceDip;

    // ── Roman numerals ────────────────────────────────────────────────
    float nMask = 0.0;
    for(int i = 1; i <= 12; i++){
        float ang  = float(i) * 0.5236;              // 2π/12, clockwise from top
        vec2  nPos = vec2(sin(ang), cos(ang)) * 0.72; // position on ring
        float nd   = glyph((uv - nPos) * 7.5, i);
        nMask += 1.0 - smoothstep(-0.018, 0.018, nd);
    }
    nMask = clamp(nMask, 0.0, 1.0);

    // ── Hands ────────────────────────────────────────────────────────
    float ha = uTime * 0.055;   // hour
    float ma = uTime * 0.66;    // minute
    vec2  hd = vec2(sin(ha), cos(ha));
    vec2  md = vec2(sin(ma), cos(ma));

    // Hour hand: thicker, shorter
    float hM  = 1.0 - smoothstep(0.0, 0.055, seg2(uv, -hd*0.08, hd*0.44));
    // Minute hand: thinner, longer
    float mM  = 1.0 - smoothstep(0.0, 0.036, seg2(uv, -md*0.10, md*0.68));
    // Center pin
    float cpM = 1.0 - smoothstep(0.0, 0.060, r);

    vec3 darkC    = vec3(0.07, 0.06, 0.05);
    float allDark = clamp(nMask + hM + mM + cpM, 0.0, 1.0);

    // ── Composition ──────────────────────────────────────────────────
    // Face: cream with dark marks
    vec3 faceDrawn = mix(faceCol, darkC, allDark);

    // Combine: face inside, rim at edge, crown on top
    vec3  col   = faceDrawn * faceM;
    col        += rimCol * rimM  * (1.0 - faceM);
    col        += crownCol * crownM * (1.0 - faceM) * (1.0 - rimM);

    float alpha = max(faceM, max(rimM, crownM));

    // Subtle glow to help show through cloud attenuation
    float glow = smoothstep(1.52, 0.95, r) * 0.15;
    col  += vec3(0.86, 0.86, 0.90) * glow;
    alpha = max(alpha, glow * 0.32);

    return vec4(col, alpha * 0.88);
}

// ── Main ─────────────────────────────────────────────────────────────

void main(){
    vec2 uv = vUV.st * 2.0 - 1.0;
    uv.y = -uv.y;
    uv.x *= 16.0/9.0;

    vec3 ro = vec3(0.5, -0.7, -4.8);
    vec3 tg = vec3(0.0,  1.8,  1.5);
    vec3 fw = normalize(tg - ro);
    vec3 rt = normalize(cross(fw, vec3(0,1,0)));
    vec3 up3= cross(rt, fw);
    vec3 rd = normalize(fw + uv.x*rt*0.70 + uv.y*up3*0.70);

    // Sky
    float sk = clamp(rd.y, 0., 1.);
    vec3 sky = mix(vec3(0.22,0.44,0.82), vec3(0.01,0.02,0.25), sk*sk*sk);
    sky = mix(vec3(0.46,0.56,0.72), sky, smoothstep(-0.04,0.22,rd.y));
    float sunD = max(0., dot(rd,SUN));
    sky += pow(sunD,350.)*vec3(1.9,1.6,0.9) + pow(sunD,10.)*vec3(0.22,0.16,0.02)*.28;

    float cosA=dot(rd,SUN), g1=.80, g2=-.12;
    float ph = .60*(1.-g1*g1)/pow(1.+g1*g1-2.*g1*cosA,1.5)/12.566
             + .40*(1.-g2*g2)/pow(1.+g2*g2-2.*g2*cosA,1.5)/12.566;

    // ── Clock plane intersection ──────────────────────────────────────
    float t_clock  = -1.0;
    vec4  ck       = vec4(0.0);
    if(abs(rd.z) > 0.0005){
        float tc = (CLK_C.z - ro.z) / rd.z;
        if(tc > 0.3 && tc < 16.0){
            vec3 hp = ro + rd * tc;
            vec4 cf = daliClock(hp.xy - CLK_C.xy, rd);
            if(cf.a > 0.004){ t_clock = tc; ck = cf; }
        }
    }

    vec3  cCol     = vec3(0.);
    float tr       = 1.0;
    float tr_atClk = -1.0;

    const int N=80; const float T0=0.30, T1=16.0, DT=(T1-T0)/float(N);
    float t = T0;
    for(int i=0; i<N; i++){
        if(tr < 0.015) break;
        if(t_clock > 0.0 && t >= t_clock && tr_atClk < 0.0) tr_atClk = tr;
        vec3  p = ro + rd * t;
        float d = cloudDen(p);
        if(d > 0.02){
            float alpha  = 1.-exp(-d*DT*3.5);
            float lit    = shadowMarch(p);
            float powder = 1.-exp(-d*DT*7.0);
            float ms     = .22*exp(-d*DT*3.);
            float hgt    = clamp((p.y+0.1)/3.5,0.,1.);
            vec3 sunC = vec3(1.05,1.01,.97)*lit*(ph*7.+.08)*powder;
            vec3 amb  = mix(vec3(.05,.09,.36),vec3(.60,.70,.96),hgt*hgt)*.60;
            cCol += tr*alpha*(sunC+amb+vec3(.50,.60,.82)*ms);
            tr   *= (1.-alpha);
        }
        t += DT;
    }
    if(t_clock > 0.0 && tr_atClk < 0.0) tr_atClk = tr;

    vec3 col = cCol + sky * tr;

    // Composite clock: 55% attenuated by clouds + 45% guaranteed minimum
    if(t_clock > 0.0 && ck.a > 0.004){
        float vis    = clamp(tr_atClk, 0., 1.) * 0.55 + 0.45;
        col = mix(col, ck.rgb, ck.a * vis);
    }

    col = col*(2.51*col+0.03)/(col*(2.43*col+0.59)+0.14);
    col = pow(clamp(col,0.,1.),vec3(1./2.2));
    fragColor = vec4(col, 1.0);
}
