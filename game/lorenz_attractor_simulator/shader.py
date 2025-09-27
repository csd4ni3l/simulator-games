import pyglet, pyglet.graphics

from pyglet.gl import GL_NEAREST

shader_source = """#version 430 core
uniform vec2 resolution;

uniform float sigma;
uniform float rho;
uniform float beta;
uniform float dt;
uniform int steps;
uniform float decay_factor;

layout (local_size_x = 32, local_size_y = 32, local_size_z = 1) in;
layout (location = 0, rgba32f) uniform image2D img_output;

vec2 project (vec3 p) {
    return (vec2(p.x + 25, p.z) * 0.02);
}

void main() {
    ivec2 texel_coord = ivec2(gl_GlobalInvocationID.xy);

    if (texel_coord.x >= int(resolution.x) || texel_coord.y >= int(resolution.y)) {
        return;
    }

    vec4 current_color = imageLoad(img_output, texel_coord);
    current_color.rgb *= decay_factor;
    imageStore(img_output, texel_coord, current_color);

    for (int seed_offset = 0; seed_offset < 4; seed_offset++) {
        float seedx = (float(texel_coord.x + seed_offset * 0.25) / resolution.x - 0.5) * 20.0;
        float seedy = (float(texel_coord.y + seed_offset * 0.25) / resolution.y - 0.5) * 20.0;
        float seedz = 15.0 + seed_offset * 2.0;

        vec3 p = vec3(seedx, seedy, seedz);

        for (int i = 0; i < steps; i++) {
            float dx = sigma * (p.y - p.x);
            float dy = p.x * (rho - p.z) - p.y;
            float dz = p.x * p.y - beta * p.z;
            
            p += vec3(dx, dy, dz) * dt;

            vec2 uv = project(p);
            ivec2 coord = ivec2(uv * resolution);

            if (coord.x >= 0 && coord.x < int(resolution.x) &&
                coord.y >= 0 && coord.y < int(resolution.y)) {

                vec4 old_color = imageLoad(img_output, coord);
                float intensity = 0.008;

                vec3 new_color = old_color.rgb + vec3(intensity, intensity * 0.6, intensity * 0.9);
                new_color = min(new_color, vec3(1.0));
                imageStore(img_output, coord, vec4(new_color, 1.0));

            }
        }
    }
}

"""

def create_shader(width, height):
    shader_program = pyglet.graphics.shader.ComputeShaderProgram(shader_source)

    lorenz_attractor_image = pyglet.image.Texture.create(width, height, internalformat=pyglet.gl.GL_RGBA32F, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)

    uniform_location = shader_program["img_output"]
    lorenz_attractor_image.bind_image_texture(unit=uniform_location)

    return shader_program, lorenz_attractor_image