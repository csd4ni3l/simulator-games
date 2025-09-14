import pyglet, pyglet.graphics

from pyglet.gl import glBindBufferBase, GL_SHADER_STORAGE_BUFFER, GL_NEAREST

from utils.constants import WATER_ROWS, WATER_COLS

shader_source = f"""#version 430 core

layout(std430, binding = 3) buffer PreviousHeights {{
    float previous_heights[{WATER_ROWS * WATER_COLS}]; 
}};

layout(std430, binding = 4) buffer CurrentHeights {{
    float current_heights[{WATER_ROWS * WATER_COLS}];
}};

uniform int rows;
uniform int cols;
uniform int splash_row;
uniform int splash_col;
uniform float damping;
uniform float wave_speed;
uniform float splash_strength;
uniform float splash_radius;

layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
layout (location = 0, rgba32f) uniform image2D img_output;

void main() {{
    ivec2 texel_coord = ivec2(gl_GlobalInvocationID.xy);

    int row = texel_coord.y * rows / imageSize(img_output).y;
    int col = texel_coord.x * cols / imageSize(img_output).x;
    int current_index = (row * cols) + col;

    if(row == 0 || col == 0 || row == rows-1 || col == cols-1) return;

    float dist = distance(vec2(row, col), vec2(splash_row, splash_col));
    if(dist <= splash_radius) current_heights[current_index] += splash_strength * (1.0 - dist / splash_radius);
        
    float laplacian = current_heights[(row - 1) * cols + col] + 
                      current_heights[(row + 1) * cols + col] +
                      current_heights[row * cols + (col - 1)] +
                      current_heights[row * cols + (col + 1)] - 
                      4.0 * current_heights[current_index];

    float dt = 0.1;

    float h_new = 2.0 * current_heights[current_index]
                  - previous_heights[current_index] +
                  (wave_speed * wave_speed)*(dt*dt) * laplacian -
                  damping * (current_heights[current_index] - previous_heights[current_index]);

    previous_heights[current_index] = current_heights[current_index];
    current_heights[current_index] = h_new;
    
    float minH = -0.5;
    float maxH = 0.5;
    float normH = clamp((h_new - minH) / (maxH - minH), 0.0, 1.0);

    imageStore(img_output, texel_coord, vec4(0.0, 0.0, normH, 1.0));
}}

"""

def create_shader():
    shader_program = pyglet.graphics.shader.ComputeShaderProgram(shader_source)

    water_image = pyglet.image.Texture.create(WATER_COLS, WATER_ROWS, internalformat=pyglet.gl.GL_RGBA32F, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)

    uniform_location = shader_program['img_output']
    water_image.bind_image_texture(unit=uniform_location)

    previous_heights_ssbo = pyglet.graphics.BufferObject(WATER_COLS * WATER_ROWS * 4, usage=pyglet.gl.GL_DYNAMIC_COPY)
    current_heights_ssbo = pyglet.graphics.BufferObject(WATER_COLS * WATER_ROWS * 4, usage=pyglet.gl.GL_DYNAMIC_COPY)
    
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 3, previous_heights_ssbo.id)
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 4, current_heights_ssbo.id)

    return shader_program, water_image, previous_heights_ssbo, current_heights_ssbo