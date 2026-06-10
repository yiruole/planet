// Cumulus Cloud v7 — Dalí Melting Clock
// Clock fix: dual-track compositing (physically attenuated + guaranteed minimum)

uniform float uTime;
uniform float uBeat;

layout(location = 0) out vec4 fragColor;

// ── Noise ────────────────────────────────────────────────────────────

float hh(float n){ return fract(sin(n)*43758.5453); }
float n3(vec3 x){
    vec3 p=floor(x), f=fract(x);
    f=f*f*(3.0-2.0*f);
    float n=p.x+p.y*57.0+113.0*p.z;
    return mix(
        mix(mix(hh(n),hh(n+1.0),f.x),mix(hh(n+57.0),hh(n+58.0),f.x),f.y),
        mix(mix(hh(n+113.0),hh(n+114.0),f.x),mix(hh(n+170.0),hh(n+171.0),f.x),f.y),
        f.z);
}
const mat3 M=mat3(0.00,0.80,0.60,-0.80,0.36,-0.48,-0.60,-0.48,0.64);
float fbm5(vec3 p){float v=0.,a=.5;p+=vec3(31.4,27.2,14.1);for(int i=0;i<5;i++){v+=a*n3(p);p=M*p*2.;a*=.5;}return v*1.032;}
float fbm4(vec3 p){float v=0.,a=.5;p+=vec3(17.3,42.1,8.09);for(int i=0;i<4;i++){v+=a*n3(p);p=M*p*2.;a*=.5;}return v*1.067;}
float fbm3(vec3 p){float v=0.,a=.5;p+=vec3(5.77,93.1,55.6);for(int i=0;i<3;i++){v+=a*n3(p);p=M*p*2.;a*=.5;}return v*1.143;}

// ── Cloud density (v6, unchanged) ────────────────────────────────────

float layerDen(vec3 pos, float yBase, vec3 seed, float ct, float zOff){
    float yL=pos.y-yBase;
    float yEnv=smoothstep(-0.05,0.12,yL)*(1.-smoothstep(1.0,1.4,yL));
    if(yEnv<.001) return 0.;
    float xFall=1.-smoothstep(3.5,6.0,abs(pos.x));
    float zFall=1.-smoothstep(2.0,4.5,abs(pos.z-zOff));
    if(xFall*zFall<.001) return 0.;
    vec3 ds=vec3(ct*.60,ct*.14,ct*.35);
    float shape =fbm4(pos*.85+seed+ds);
    float detail=fbm5(pos*2.1+seed*.44+vec3(-ct*1.15,ct*.90,ct*1.50))*.21;
    float fine  =n3(pos*4.6+seed*.28+vec3(ct*3.,ct*1.6,ct*2.3))*.10;
    float excess=max(0.,shape+detail+fine-0.55);
    return min(excess*45.,6.)*yEnv*xFall*zFall;
}
float shadowDen(vec3 pos){
    float yEnv=smoothstep(-.3,.2,pos.y)*(1.-smoothstep(4.2,5.,pos.y));
    if(yEnv<.001) return 0.;
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
          +layerDen(pos,1.50,vec3(19.3,11.7, 7.3),ct*1.22,2.0)
          +layerDen(pos,2.85,vec3(38.6,24.1,15.5),ct*1.45,5.0);
}

// ── Dalí Melting Clock ───────────────────────────────────────────────
// Plane: z = CLK_C.z, facing camera
// Melting: bottom droops down, sides wobble

const vec3  CLK_C = vec3(0.0, 1.95, 2.0);
const float CLK_R = 0.70;   // radius in world units — large for visibility

float seg2(vec2 p, vec2 a, vec2 b){
    vec2 pa=p-a, ba=b-a;
    return length(pa-ba*clamp(dot(pa,ba)/dot(ba,ba),0.,1.));
}

// Unmelt: maps a screen-space position on the clock plane back to
// the "original" clock face UV (inverse of the melt deformation)
vec2 unmelt(vec2 q){
    // Only bottom half droops (q.y < 0.06 in local clock space)
    float droop=max(0., -(q.y - 0.06));
    q.y += droop * droop * 0.42;
    // Sideways wobble, only on melted bottom region
    float bottomBlend = smoothstep(0.06, -0.50, q.y);
    q.x += sin(q.y * 2.8 + uTime * 0.28) * 0.065 * bottomBlend;
    return q;
}

vec4 daliClock(vec2 q){
    // q = world XY offset from clock center (already on z=CLK_C.z plane)
    vec2  uv = unmelt(q) / CLK_R;   // normalized [-1..1]
    float r  = length(uv);
    if(r > 1.28) return vec4(0.0);

    // ── Geometry masks ──
    float faceM = smoothstep(1.06, 0.96, r);
    // Rim = ring between r=0.97 and r=1.22
    float rimM  = smoothstep(1.25, 1.14, r) * smoothstep(0.96, 1.06, r);

    // ── Hands ──
    float ha = uTime * 0.07;         // hour: slow rotation
    float ma = uTime * 0.87;         // minute: faster
    vec2  hd = vec2(sin(ha), cos(ha));
    vec2  md = vec2(sin(ma), cos(ma));
    float hhm = 1.-smoothstep(0., 0.070, seg2(uv, -hd*0.10, hd*0.44));
    float mhm = 1.-smoothstep(0., 0.046, seg2(uv, -md*0.12, md*0.68));

    // ── 12 hour markers ──
    float mk = 0.;
    for(int i=0; i<12; i++){
        float a = float(i) * 0.5236;   // 2π/12
        vec2  o = vec2(sin(a), cos(a));
        mk += 1.-smoothstep(0., 0.056, seg2(uv, o*0.74, o*0.89));
    }
    mk = clamp(mk, 0., 1.);

    // ── Center pin ──
    float cp = 1.-smoothstep(0., 0.072, r);

    // ── Colors ──
    // Over-bright ivory so it survives cloud attenuation and tone-map
    float lx = 0.80 + 0.20*uv.x - 0.10*uv.y;   // simple directional shading
    vec3 col = vec3(1.30, 1.26, 1.15) * lx;      // bright ivory face
    col = mix(col, vec3(0.06, 0.05, 0.04), clamp(hhm+mhm+cp+mk, 0., 1.));
    col = mix(col, vec3(1.08, 1.11, 1.15)*lx, rimM);  // bright silver rim

    float alpha = max(faceM, rimM) * 0.84;

    // Outer glow — extends past rim, helps clock "glow through" clouds
    float glow = smoothstep(1.55, 0.95, r) * 0.22;
    col  += vec3(0.92, 0.85, 0.70) * glow;
    alpha = max(alpha, glow * 0.45);

    return vec4(col, alpha);
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
    float sunD = max(0., dot(rd, SUN));
    sky += pow(sunD,350.)*vec3(1.9,1.6,0.9) + pow(sunD,10.)*vec3(0.22,0.16,0.02)*0.28;

    float cosA=dot(rd,SUN), g1=.80, g2=-.12;
    float ph = .60*(1.-g1*g1)/pow(1.+g1*g1-2.*g1*cosA,1.5)/12.566
             + .40*(1.-g2*g2)/pow(1.+g2*g2-2.*g2*cosA,1.5)/12.566;

    // ── Clock plane intersection ──
    // Ray hits z = CLK_C.z when: ro.z + rd.z*t = CLK_C.z
    float t_clock = -1.0;
    vec4  ck      = vec4(0.);
    if(abs(rd.z) > 0.0005){
        float tc = (CLK_C.z - ro.z) / rd.z;
        if(tc > 0.3 && tc < 16.0){
            vec3 hp = ro + rd * tc;
            vec4 cf = daliClock(hp.xy - CLK_C.xy);
            if(cf.a > 0.004){ t_clock = tc; ck = cf; }
        }
    }

    vec3  cCol      = vec3(0.);
    float tr        = 1.0;
    float tr_atClk  = -1.0;   // transmittance at clock depth; -1 = not yet reached

    const int   N  = 80;
    const float T0 = 0.30, T1 = 16.0, DT = (T1-T0)/float(N);

    float t = T0;
    for(int i=0; i<N; i++){
        if(tr < 0.015) break;

        // Snapshot transmittance at clock depth (first crossing only)
        if(t_clock > 0.0 && t >= t_clock && tr_atClk < 0.0)
            tr_atClk = tr;

        vec3  p = ro + rd * t;
        float d = cloudDen(p);
        if(d > 0.02){
            float alpha  = 1.-exp(-d*DT*3.5);
            float lit    = shadowMarch(p);
            float powder = 1.-exp(-d*DT*7.0);
            float ms     = 0.22*exp(-d*DT*3.);
            float hgt    = clamp((p.y+0.1)/3.5, 0., 1.);
            vec3 sunC = vec3(1.05,1.01,.97)*lit*(ph*7.+.08)*powder;
            vec3 amb  = mix(vec3(.05,.09,.36), vec3(.60,.70,.96), hgt*hgt)*.60;
            cCol += tr*alpha*(sunC+amb+vec3(.50,.60,.82)*ms);
            tr   *= (1.-alpha);
        }
        t += DT;
    }

    // Handle clock past last step
    if(t_clock > 0.0 && tr_atClk < 0.0) tr_atClk = tr;

    vec3 col = cCol + sky * tr;

    // ── Composite clock ──
    // Dual-track: 55% physically attenuated (clouds in front reduce it),
    //             45% guaranteed minimum so clock is never invisible.
    if(t_clock > 0.0 && ck.a > 0.004){
        float vis    = clamp(tr_atClk, 0., 1.) * 0.55 + 0.45;
        float factor = ck.a * vis;
        col = mix(col, ck.rgb, factor);
    }

    col = col*(2.51*col+0.03)/(col*(2.43*col+0.59)+0.14);
    col = pow(clamp(col, 0., 1.), vec3(1./2.2));
    fragColor = vec4(col, 1.0);
}
