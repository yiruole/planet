// Cumulus Cloud Raymarcher v6 — Individual Puffs, Sharp Edges, Fast Morph
// ROOT FIXES vs v4/v5:
//   1. Shape scale 0.85 (was 0.42/0.54) → individual visible cloud puffs
//   2. Linear excess*45 (not pow(x,1.5)) → instant sharp edge
//   3. Beer-Lambert coeff 3.5 (not 14) → doesn't over-saturate, lets sharpness show
//   4. 3 layers at different z-depths → "层叠" perspective parallax
//   5. Large drift velocities → clouds visibly move and morph every second

uniform float uTime;
uniform float uBeat;

layout(location = 0) out vec4 fragColor;

float hh(float n){ return fract(sin(n)*43758.5453); }
float n3(vec3 x){
    vec3 p=floor(x), f=fract(x);
    f=f*f*(3.0-2.0*f);
    float n=p.x+p.y*57.0+113.0*p.z;
    return mix(
        mix(mix(hh(n),hh(n+1.0),f.x), mix(hh(n+57.0),hh(n+58.0),f.x), f.y),
        mix(mix(hh(n+113.0),hh(n+114.0),f.x), mix(hh(n+170.0),hh(n+171.0),f.x), f.y),
        f.z);
}

const mat3 M = mat3(
     0.00,  0.80,  0.60,
    -0.80,  0.36, -0.48,
    -0.60, -0.48,  0.64);

float fbm5(vec3 p){
    float v=0.0,a=0.5; p+=vec3(31.4,27.2,14.1);
    for(int i=0;i<5;i++){ v+=a*n3(p); p=M*p*2.0; a*=0.5; }
    return v*1.032;
}
float fbm4(vec3 p){
    float v=0.0,a=0.5; p+=vec3(17.3,42.1,8.09);
    for(int i=0;i<4;i++){ v+=a*n3(p); p=M*p*2.0; a*=0.5; }
    return v*1.067;
}
float fbm3(vec3 p){
    float v=0.0,a=0.5; p+=vec3(5.77,93.1,55.6);
    for(int i=0;i<3;i++){ v+=a*n3(p); p=M*p*2.0; a*=0.5; }
    return v*1.143;
}

// One cloud layer — sharp puffs, clearly separated from sky
// yBase: height center, seed: noise seed vector, ct: cloud time, zOff: depth offset
float layerDen(vec3 pos, float yBase, vec3 seed, float ct, float zOff){
    float yL = pos.y - yBase;
    // Sharp flat base (real cumulus), soft top
    float yEnv = smoothstep(-0.05, 0.12, yL) * (1.0 - smoothstep(1.0, 1.4, yL));
    if(yEnv < 0.001) return 0.0;

    // Wide x, bounded z — panoramic horizontal coverage
    float xFall = 1.0 - smoothstep(3.5, 6.0, abs(pos.x));
    float zFall = 1.0 - smoothstep(2.0, 4.5, abs(pos.z - zOff));
    float hEnv  = xFall * zFall;
    if(hEnv < 0.001) return 0.0;

    // SHAPE: scale 0.85 → individual puff diameter ~1.2 world units
    // Previous shaders used 0.42 which created ONE giant smooth blob
    vec3 d_s = vec3(ct*0.60,  ct*0.14,  ct*0.35);
    float shape = fbm4(pos*0.85 + seed + d_s);

    // DETAIL: higher freq, different direction → surface morphing
    vec3 d_d = vec3(-ct*1.15,  ct*0.90,  ct*1.50);
    float detail = fbm5(pos*2.1 + seed*0.44 + d_d) * 0.21;

    // FINE bumps
    float fine = n3(pos*4.6 + seed*0.28 + vec3(ct*3.0, ct*1.6, ct*2.3)) * 0.10;

    float raw    = shape + detail + fine;
    float excess = max(0.0, raw - 0.55);

    // LINEAR * 45 = instant steep cliff at cloud surface
    // pow(excess,1.5) from v4 had zero derivative at 0 — that caused all the blur
    return min(excess * 45.0, 6.0) * yEnv * hEnv;
}

// Fast shadow approximation — single fbm3 covers whole volume
float shadowDen(vec3 pos){
    float yEnv = smoothstep(-0.3, 0.2, pos.y) * (1.0 - smoothstep(4.2, 5.0, pos.y));
    if(yEnv < 0.001) return 0.0;
    float ct = uTime;
    float s = fbm3(pos*0.85 + vec3(ct*0.60, ct*0.14, ct*0.35));
    float e = max(0.0, s - 0.52);
    return min(e * 35.0, 5.0) * yEnv;
}

const vec3 SUN = vec3(0.4497, 0.8797, 0.1499);

float shadowMarch(vec3 p){
    float acc=0.0, s=0.09;
    for(int i=0;i<5;i++){ p+=SUN*s; acc+=shadowDen(p)*s; s*=1.7; }
    return exp(-acc * 9.0);
}

float cloudDen(vec3 pos){
    float ct = uTime;
    vec3 s0=vec3( 0.00,  0.00,  0.00);
    vec3 s1=vec3(19.30, 11.70,  7.30);
    vec3 s2=vec3(38.60, 24.10, 15.50);
    // 3 layers: different heights AND z-depths for perspective stacking
    float d  = layerDen(pos,  0.10, s0, ct,        -0.5);
    d       += layerDen(pos,  1.50, s1, ct * 1.22,  2.0);
    d       += layerDen(pos,  2.85, s2, ct * 1.45,  5.0);
    return d;
}

void main(){
    vec2 uv = vUV.st * 2.0 - 1.0;
    uv.x *= 16.0/9.0;

    // Camera below cloud base, looking up into the towers
    vec3 ro = vec3(0.5, -0.7, -4.8);
    vec3 tg = vec3(0.0,  1.8,  1.5);
    vec3 fw = normalize(tg - ro);
    vec3 rt = normalize(cross(fw, vec3(0,1,0)));
    vec3 up3 = cross(rt, fw);
    vec3 rd  = normalize(fw + uv.x*rt*0.70 + uv.y*up3*0.70);

    // DEEP BLUE sky
    float sk = clamp(rd.y, 0.0, 1.0);
    vec3 sky = mix(vec3(0.22, 0.44, 0.82), vec3(0.01, 0.02, 0.25), sk*sk*sk);
    sky = mix(vec3(0.46, 0.56, 0.72), sky, smoothstep(-0.04, 0.22, rd.y));
    float sunD = max(0.0, dot(rd, SUN));
    sky += pow(sunD, 350.0) * vec3(1.9, 1.6, 0.9);
    sky += pow(sunD,  10.0) * vec3(0.22, 0.16, 0.02) * 0.28;

    float cosA = dot(rd, SUN);
    float g1=0.80, g2=-0.12;
    float ph = 0.60*(1.0-g1*g1)/pow(1.0+g1*g1-2.0*g1*cosA,1.5)/12.566
             + 0.40*(1.0-g2*g2)/pow(1.0+g2*g2-2.0*g2*cosA,1.5)/12.566;

    vec3  cCol = vec3(0.0);
    float tr   = 1.0;

    const int   N  = 80;
    const float T0 = 0.30;
    const float T1 = 16.0;
    const float DT = (T1 - T0) / float(N);

    float t = T0;
    for(int i=0; i<N; i++){
        if(tr < 0.015) break;
        vec3  p = ro + rd * t;
        float d = cloudDen(p);
        if(d > 0.02){
            // coeff=3.5: at cloud edge (d=1), alpha≈0.42/step → crisp in 2-3 steps
            //            at cloud center (d=5), alpha≈0.94 → opaque instantly
            float alpha  = 1.0 - exp(-d * DT * 3.5);
            float lit    = shadowMarch(p);
            float powder = 1.0 - exp(-d * DT * 7.0);
            float ms     = 0.22 * exp(-d * DT * 3.0);
            float hgt    = clamp((p.y + 0.1) / 3.5, 0.0, 1.0);

            // Dramatic contrast: near-white bright top, deep blue-grey shadow base
            vec3 sunC = vec3(1.05, 1.01, 0.97) * lit * (ph*7.0 + 0.08) * powder;
            vec3 amb  = mix(vec3(0.05, 0.09, 0.36),   // dark shadow bottom
                            vec3(0.60, 0.70, 0.96),   // bright lit top
                            hgt*hgt) * 0.60;
            vec3 msC  = vec3(0.50, 0.60, 0.82) * ms;

            cCol += tr * alpha * (sunC + amb + msC);
            tr   *= (1.0 - alpha);
        }
        t += DT;
    }

    vec3 col = cCol + sky * tr;
    col = col*(2.51*col + 0.03) / (col*(2.43*col + 0.59) + 0.14);
    col = pow(clamp(col, 0.0, 1.0), vec3(1.0/2.2));
    fragColor = vec4(col, 1.0);
}
