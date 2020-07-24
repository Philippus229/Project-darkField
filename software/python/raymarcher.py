import numpy as np
import moderngl, random, imageio
import moderngl_window as mglw

math_pi = 3.141592654

VERTEX_SHADER = '''
#version 430

in vec2 in_vert;

void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
'''

FRAGMENT_SHADER = '''
#version 430

#define PI 3.141592654

//WU=world units (blocks)
#define ML_WIDTH 33.59788359788 //microlens pitch/diameter (px)
#define RATIO_WH 1.154700538 //2*sqrt(3)/3
#define ML_WIDTH_WU 0.05 //microlens pitch/diameter (wu)
#define MLA_SIZE 18000 //for hexagonal MLA (lenses per side)
#define MLA_IOR 1.6 //MLA's index of refraction
#define THICC_RAT 1 //ratio of microlenses' height to width

const float ML_HEIGHT = ML_WIDTH*RATIO_WH;

#define NEAR 2 //near culling distance behind (technically above) camera/microlens layer
#define HIT_DIST 0.01
#define MAX_DIST 10
#define MAX_ITERS 100

uniform uvec2 w_size;
uniform vec3 cpos;

layout(origin_upper_left) in vec4 gl_FragCoord;
out vec4 f_color;

#define SCENE 1 //which scene to render

float sphereSDF(vec3 cp, vec3 op, float or) {
    return length(cp-op)-or;
}

float boxSDF(vec3 cp, vec3 op, vec3 os) {
    vec3 pd = abs(op-cp);
    vec3 td = max(vec3(0), pd-os/2.0);
    return length(td);
}

float planeSDF(vec3 cp, vec3 op, vec2 os) {
    vec3 pd = abs(op-cp);
    vec2 td = max(vec2(0), pd.xz-os/2.0);
    return length(vec3(td, pd.y));
}

float thingSDF(vec3 cp, vec3 op) {
    return min(min(sphereSDF(cp,op+vec3(-1,-1,0),0.25), sphereSDF(cp,op+vec3(0),0.25)), sphereSDF(cp,op+vec3(1,1,0),0.25));
}

vec4 thingColor(vec3 cp) {
    return (cp.x < -0.5 ? vec4(1,0,0,1) : (cp.x < 0.5 ? vec4(0,1,0,1) : vec4(0,0,1,1)));
}

float sceneSDF(vec3 pos) {
    if (SCENE == 0) {
        return min(min(sphereSDF(pos, vec3( 1.0, -0.5,  0.0 ), 0.5),
                       boxSDF   (pos, vec3(-1.0, -0.5,  0.0 ), vec3(1))),
                       planeSDF (pos, vec3( 0.0, -1.0,  0.0 ), vec2(10)));
    } else if (SCENE == 1) {
        return min(planeSDF(pos, vec3( 0.0, -2.0,  0.0 ), vec2(10)),
                   thingSDF(pos, vec3( 0.0,  0.0,  0.0 )));
    }
}

vec4 sceneColor(vec3 pos) {
    if (SCENE == 0) {
        return (pos.y > HIT_DIST-1.0 ? (pos.x > 0.0 ? vec4(1.0, 0.5, 0.0, 1.0) : vec4(0.5, 1.0, 0.5, 1.0)) : vec4(vec3(0.25+0.75*mod(floor(0.0-pos.x)+floor(0.0-pos.z), 2)), 1.0));
    } else if (SCENE == 1) {
        return (pos.y > HIT_DIST-2.0 ? thingColor(pos) : vec4(vec3(0.25+0.75*mod(floor(pos.x)+floor(pos.z), 2)), 1.0));
    }
}

vec4 lights[2][2] = {
    { vec4(5.0, 5.0, 3.0, 5.0), vec4(1.0, 1.0, 1.0, 0.75) },
    { vec4(5.0,  10, 7.0, 5.0), vec4(1.0, 1.0, 1.0, 2.0) }
};

vec3 getLighting(vec3 hpos, bool shadows, float closest) {
    vec3 lighting = vec3(0);
    for (int li=0; li<lights.length(); li++) {
        float br = pow(length(lights[li][0].xyz-hpos)/lights[li][0].w, -2);
        if (shadows) {
            vec3 ldir = normalize(lights[li][0].xyz-hpos);
            vec3 hpos0 = hpos; //for some reason the value of br changed when changing hpos, but I guess that's just how GLSL works
            for (float sdist = closest; sdist <= length(lights[li][0].xyz-hpos); hpos0 += ldir*sdist) {
                sdist = sceneSDF(hpos0);
                if (sdist < closest) {
                    br *= 0.125; //weird ambient lighting
                    break;
                }
            }
        }
        lighting += lights[li][1].xyz*lights[li][1].w*br;
    }
    return lighting;
}

vec4 getColor(vec3 pos, int lightingType) {
    vec4 color = sceneColor(pos);
    if (lightingType == 0) {
        return color;
    } else {
        return min(vec4(1), color*vec4(getLighting(pos, lightingType == 2, sceneSDF(pos)), 1.0));
    }
}

vec4 marchRay(vec3 rpos, vec3 rdir) {
    for (int i=0; i<MAX_ITERS; i++) {
        float dist = sceneSDF(rpos);
        if (dist < HIT_DIST) {
            return getColor(rpos, 1);
        } else if (dist > MAX_DIST) {
            break;
        }
        rpos += rdir*dist;
    }
    return vec4(0.125, 0.125, 0.125, 1.0);
}

void main() {
    vec2 new_coord = gl_FragCoord.xy-(w_size-vec2(ML_WIDTH, ML_HEIGHT))/2.0;
    
    float lens_row = floor(new_coord.y/(3.0*ML_HEIGHT/4.0));
    float loc_y = new_coord.y-lens_row*3.0*ML_HEIGHT/4.0;
    if (loc_y < ML_HEIGHT/4.0) {
        float lim_offset = abs(ML_HEIGHT/4.0-0.5*ML_HEIGHT*mod(new_coord.x+mod(abs(lens_row),2)*ML_WIDTH/2.0,ML_WIDTH)/ML_WIDTH);
        if (loc_y < lim_offset) {
            lens_row--;
            loc_y += 3.0*ML_HEIGHT/4.0;
        }
    }
    loc_y -= ML_HEIGHT/2.0;
    
    float parity = mod(abs(lens_row),2);
    float lens_col = floor((new_coord.x+parity*ML_WIDTH/2.0)/ML_WIDTH) - 0.5*parity;
    float loc_x = new_coord.x-(lens_col+0.5)*ML_WIDTH;
    
    if ((abs(lens_row) >= MLA_SIZE) || (abs(lens_col) >= float(MLA_SIZE)-abs(lens_row/2.0))) {
        f_color = vec4(0);
        return;
    }
    
    vec2 mlc = vec2(lens_col*ML_WIDTH_WU, 3.0*lens_row*RATIO_WH*ML_WIDTH_WU/4.0);
    vec2 uv = vec2(loc_x/ML_WIDTH, loc_y/ML_WIDTH);

    float yd0 = -1.0;
    float xd0 = tan(asin(atan(uv.x/THICC_RAT)/MLA_IOR));
    float zd0 = tan(asin(atan(uv.y/THICC_RAT)/MLA_IOR));
    
    float oy = cpos.y+NEAR;
    float ox = cpos.x+mlc.x-xd0*NEAR;
    float oz = cpos.z+mlc.y-zd0*NEAR;
    
    f_color = marchRay(vec3(ox,oy,oz), normalize(vec3(xd0,yd0,zd0)));
    //f_color = vec4(vec3(0.5)+normalize(vec3(xd0,zd0,-yd0))/2.0, 1.0); //MLA normal map
}
'''

class RayMarcher(mglw.WindowConfig):
    title = "Ray Marcher"
    gl_version = (4, 3)
    #cursor = False
    window_size = (2560, 1440)
    aspect_ratio = (window_size[0]/window_size[1])
    resizable = False
    position = (0, 0)
    samples = 8

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prog = self.ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)
        
        self.w_size = self.prog["w_size"]
        self.cpos = self.prog["cpos"]
        
        vertices = np.array([-1.0,-1.0,  -1.0, 1.0,   1.0,-1.0,   1.0, 1.0 ])
        self.vbo = self.ctx.buffer(vertices.astype("f4"))
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, "in_vert")

    def render(self, time, frame_time):
        self.ctx.clear(0.0, 0.0, 0.0)
        self.w_size.value = self.wnd.size
        self.cpos.value = (0.0, 0.0, 0.0) #camera position (center)
        self.vao.render(moderngl.TRIANGLE_STRIP)
        if self.wnd.frames == 0:
            output = np.frombuffer(self.wnd.fbo.read(components=3, dtype="f1"), dtype=np.ubyte).reshape((self.wnd.fbo.height, self.wnd.fbo.width, 3))
            imageio.imwrite("render.png", output)

mglw.run_window_config(RayMarcher)
