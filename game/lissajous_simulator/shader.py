import pyglet, pyglet.graphics

from pyglet.gl import GL_NEAREST

shader_source = """#version 430 core

uniform float x_amp;
uniform float y_amp;
uniform float x_freq;
uniform float y_freq;
uniform float phase_shift;

uniform float thickness;
uniform int samples;
uniform float time;
uniform vec2 resolution;

layout (local_size_x = 32, local_size_y = 32, local_size_z = 1) in;
layout (location = 0, rgba32f) uniform image2D img_output;

vec2 lissajous(float t) {
    return vec2(
        x_amp * sin(x_freq * t + phase_shift + time),
        y_amp * sin(y_freq * t)
    );
}

float curve_distribution(vec2 uv) {
    float d = 1e5;

    for (int i = 0; i < samples; i++) {
        float t = float(i) / float(samples) * 6.28318;
        vec2 p = lissajous(t);
        d = min(d, length(uv - p));
    }

    return d;
}

void main() {
    ivec2 texel_coord = ivec2(gl_GlobalInvocationID.xy);

    vec2 uv = (vec2(texel_coord) / resolution) * 2.0 - 1.0;
    uv.x *= float(resolution.x) / float(resolution.y);

    float d = curve_distribution(uv);

    float line = smoothstep(thickness, thickness * 0.3, d);

    vec4 color = vec4(vec3(line), 1.0);
    imageStore(img_output, texel_coord, color);
}
"""

def create_shader(width, height):
    shader_program = pyglet.graphics.shader.ComputeShaderProgram(shader_source)

    lissajous_image = pyglet.image.Texture.create(width, height, internalformat=pyglet.gl.GL_RGBA32F, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)

    uniform_location = shader_program["img_output"]
    lissajous_image.bind_image_texture(unit=uniform_location)

    return shader_program, lissajous_image