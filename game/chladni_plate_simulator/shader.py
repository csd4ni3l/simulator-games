import pyglet, pyglet.graphics

from pyglet.gl import glBindBufferBase, GL_SHADER_STORAGE_BUFFER, GL_NEAREST

shader_source = """#version 430 core

layout (std430, binding = 3) buffer Sources {
    vec2 sources[];
};

uniform int source_count;
uniform float k;

layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
layout (location = 0, rgba32f) uniform image2D img_output;

void main() {
    ivec2 texel_coord = ivec2(gl_GlobalInvocationID.xy);
    vec2 texel_pos_float = vec2(texel_coord);

    float total_wave_height = 0.0;

    for (int i = 0; i < source_count; i++) {
        total_wave_height += cos(k * distance(texel_pos_float, sources[i]));
    }

    vec4 color;
    
    float normalized_height = total_wave_height / float(source_count);
    float value = abs(normalized_height);

    if (value > 0.9) {
        color = vec4(1.0, 0.0, 0.0, 1.0);
    } else if (value > 0.6) {
        color = vec4(1.0, 1.0, 0.0, 1.0);
    } else if (value > 0.3) {
        color = vec4(0.0, 1.0, 0.0, 1.0);
    } else {
        color = vec4(0.0, 0.0, 0.0, 1.0);
    }

    imageStore(img_output, texel_coord, color);
}
"""

def create_shader(width, height):
    shader_program = pyglet.graphics.shader.ComputeShaderProgram(shader_source)

    chladni_plate_image = pyglet.image.Texture.create(width, height, internalformat=pyglet.gl.GL_RGBA32F, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)

    uniform_location = shader_program['img_output']
    chladni_plate_image.bind_image_texture(unit=uniform_location)

    sources_ssbo = pyglet.graphics.BufferObject(32 * 8, usage=pyglet.gl.GL_DYNAMIC_COPY)
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 3, sources_ssbo.id)

    return shader_program, chladni_plate_image, sources_ssbo