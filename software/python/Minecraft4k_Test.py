import numpy as np
import moderngl, random, imageio, tkinter
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
#define ML_WIDTH 33.59788359788 //microlens picth/diameter (px)
#define RATIO_WH 1.154700538 //2*sqrt(3)/3
#define ML_WIDTH_WU 0.05 //microlens pitch/diameter (wu)
#define ML_FOV_DEG 90.0 //microlens field of view in degrees
#define MLA_SIZE 18

const float ML_HEIGHT = ML_WIDTH*RATIO_WH;
const float uv_mul = tan(PI*ML_FOV_DEG/360.0);

uniform sampler2D texmap;
uniform sampler3D blocks;
uniform uvec2 w_size;

uniform vec3 cpos;
uniform vec4 ctri; //cos(xRot), sin(xRot), cos(yRot), sin(yRot)

layout(origin_upper_left) in vec4 gl_FragCoord;
out vec4 f_color;

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
        f_color = vec4(0.0, 0.0, 0.0, 0.0);
        return;
    }
    
    vec2 mlc = vec2(lens_col*ML_WIDTH_WU, 3.0*lens_row*RATIO_WH*ML_WIDTH_WU/4.0);
    float ox = cpos.x+mlc.x*ctri.z+mlc.y*ctri.y*ctri.w;
    float oy = cpos.y+mlc.y*ctri.x;
    float oz = cpos.z-mlc.x*ctri.w+mlc.y*ctri.y*ctri.z;
    
    vec2 uv = uv_mul*vec2(loc_x/ML_WIDTH, loc_y/ML_WIDTH);
    float zd0 = ctri.x+uv.y*ctri.y;
    float yd0 = uv.y*ctri.x-ctri.y;
    float xd0 = uv.x*ctri.z+zd0*ctri.w;
    zd0 = zd0*ctri.z-uv.x*ctri.w;
    
    vec4 col = vec4(0.0, 0.0, 0.0, 1.0);
    float br = 1.0;
    float ddist = 0.0;
    float closest = 32.0;
    for (int d=0; d<3; d++) {
        float dimLength, initial;
        if      (d == 0) { dimLength = xd0; initial = ox-floor(ox); }
        else if (d == 1) { dimLength = yd0; initial = oy-floor(oy); }
        else             { dimLength = zd0; initial = oz-floor(oz); }
        float ll = 1.0/abs(dimLength);
        float xd = xd0*ll;
        float yd = yd0*ll;
        float zd = zd0*ll;
        if (dimLength > 0) initial = 1.0-initial;
        float dist = ll*initial;
        float xp = ox+xd*initial;
        float yp = oy+yd*initial;
        float zp = oz+zd*initial;
        if (dimLength < 0) {
            if (d == 0) xp--;
            if (d == 1) yp--;
            if (d == 2) zp--;
        }
        while (dist < closest) {
            int blockID = int(255.0*texelFetch(blocks, ivec3(int(xp)&63, int(yp)&63, int(zp)&63), 0).r);
            if (blockID > 0) {
                int u = int((xp+zp)*16.0) & 15;
                int v = (int(yp*16.0) & 15) + 16;
                if (d == 1) {
                    u = int(xp*16.0) & 15;
                    v = int(zp*16.0) & 15;
                    if (yd < 0) v += 2*16;
                }
                vec4 cc = texelFetch(texmap, ivec2(u+blockID*16, v), 0).rgba;
                if (cc.w > 0) {
                    col = cc;
                    ddist = 1-dist/32.0;
                    br = (255.0-mod(d+2,3)*50.0)/255.0;
                    closest = dist;
                }
            }
            xp += xd;
            yp += yd;
            zp += zd;
            dist += ll;
        }
    }
    f_color = br*ddist*col;
}
'''

def get_textures():
    texmap = np.zeros((16*16,3*16,4), dtype=np.ubyte)
    for b in range(16):
        k = 255-random.randint(0,96)
        for v in range(3*16):
            for u in range(16):
                i1, i2 = 0x966C4A, 0
                if b != 4 or random.randint(0,3) < 1: k = 255-random.randint(0,96)
                if b == 1: #grass
                    tmp = (((u*(u*3+81))>>2)&0x3)+19-v
                    if tmp > 1: i1 = 0x6AAA40
                    elif tmp > 0: k *= 2/3
                elif b == 4: i1 = 0x7F7F7F #stone
                elif b == 5: i1 = 0xB53A15+0x77590*(0 in [(u+int(v/4)*4)%8,v%4]) #brick
                elif b == 7: i1,k = [(0x675231, k*(1+(0.5-(u&0x1))*(random.randint(0,2)<1))), #log
                    (0xBC9862, 196-random.randint(0,32)+(max(abs(u-7)+(u<7),abs((v&0xF)-7)+((v&0xF)<7))%3)*32)][u in range(1,15) and v%32 in range(1,15)]
                i2 = k/((v>31)+1)
                if b == 8: i1,i2 = [(0,255),(5298487,i2)][random.randint(0,2)>0] #leaves
                texmap[u+b*16, v] = [int(((i1>>16)&0xFF)*i2/255), int(((i1>>8)&0xFF)*i2/255), int((i1&0xFF)*i2/255), 255*(0 not in [i1,i2])]
    return texmap

def get_blocks():
    blocks = np.zeros((64,64,64), dtype=np.ubyte)
    for i in range(64*64*64):
        x,y,z = i//(64*64), (i//64)%64, i%64
        blocks[x,y,z] = random.randint(0,16)*(random.uniform(0,1) < np.sqrt(np.sqrt(((y-32.5)**2+(z-32.5)**2)*0.16))-0.8)
    return blocks

class Minecraft4k(mglw.WindowConfig):
    title = "Minecraft4k - Light Field Test"
    gl_version = (4, 3)
    cursor = False
    #fullscreen = True
    root = tkinter.Tk()
    window_size = (root.winfo_screenwidth()-2, root.winfo_screenheight()-72)
    root.destroy()
    aspect_ratio = (window_size[0]/window_size[1])
    resizable = False
    position = (0, 0)
    samples = 8
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prog = self.ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)

        self.w_size = self.prog["w_size"]
        self.cpos = self.prog["cpos"]
        self.ctri = self.prog["ctri"]
        
        vertices = np.array([-1.0, -1.0,
                             -1.0,  1.0,
                              1.0, -1.0,
                              1.0,  1.0 ])
        self.vbo = self.ctx.buffer(vertices.astype("f4"))
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, "in_vert")
        
        self.texmap = get_textures()
        #imageio.imwrite("texmap.png", self.texmap)
        self.texmap_pix = bytes([c for y in range(3*16) for x in range(16*16) for c in self.texmap[x,y]])
        self.texmap_tex = self.ctx.texture((16*16,3*16), 4, self.texmap_pix)

        self.blocks = get_blocks()
        self.blocks_pix = bytes([self.blocks[x,y,z] for z in range(64) for y in range(64) for x in range(64)])
        self.blocks_tex = self.ctx.texture3d((64,64,64), 1, self.blocks_pix)
        
        self.prog["texmap"].value = 0
        self.prog["blocks"].value = 1

    def render(self, time, frame_time):
        self.ctx.clear(0.0, 0.0, 0.0)
        self.texmap_tex.use(0)
        self.blocks_tex.use(1)
        self.w_size.value = self.wnd.size
        now = (time%25)/25
        self.cpos.value = (32.5+now*64.0, 32.5, 32.5)
        yRot = np.sin(now*math_pi*2.0)*0.4+math_pi/2.0
        xRot = np.cos(now*math_pi*2.0)*0.4
        self.ctri.value = (np.cos(xRot), np.sin(xRot), np.cos(yRot), np.sin(yRot))
        self.vao.render(moderngl.TRIANGLE_STRIP)

mglw.run_window_config(Minecraft4k)
