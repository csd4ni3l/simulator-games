import pyglet, pyglet.graphics

from pyglet.gl import GL_NEAREST, glBindBufferBase, GL_SHADER_STORAGE_BUFFER

shader_source = """#version 430 core

layout (std430, binding = 3) buffer Points {
    vec2 points[];
};

uniform int point_count;
uniform vec2 resolution;
uniform float edge_thickness;
uniform float edge_smoothness;

layout (local_size_x = 32, local_size_y = 32, local_size_z = 1) in;
layout (location = 0, rgba32f) uniform image2D img_output;

vec3 hash3(float p) {
    vec3 p3 = vec3(p * 127.1, p * 311.7, p * 74.7);
    return fract(sin(p3) * 43758.5453123);
}

void main() {
    ivec2 texel_coord = ivec2(gl_GlobalInvocationID.xy);
    vec2 uv = vec2(texel_coord) / resolution;

    float min_dist = 1e5;
    float second_min = 1e5;
    int closest_id = 0;

    for (int i = 0; i < point_count; i++) {
        vec2 point = points[i] / resolution;
        float dist = length(uv - point);

        if (dist < min_dist) {
            second_min = min_dist;
            min_dist = dist;
            closest_id = i;
        }
        else if (dist < second_min) {
            second_min = dist;
        }
    }

    float edge_dist = second_min - min_dist;
    float edge = 1.0 - smoothstep(edge_thickness - edge_smoothness, edge_thickness + edge_smoothness, edge_dist);

    vec3 cell_color = hash3(float(closest_id));
    vec3 color = mix(cell_color, vec3(0.0), edge);

    imageStore(img_output, texel_coord, vec4(color, 1.0));
}
"""

def create_shader(width, height):
    shader_program = pyglet.graphics.shader.ComputeShaderProgram(shader_source)

    voronoi_diagram_image = pyglet.image.Texture.create(width, height, internalformat=pyglet.gl.GL_RGBA32F, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)

    uniform_location = shader_program["img_output"]
    voronoi_diagram_image.bind_image_texture(unit=uniform_location)

    points_ssbo = pyglet.graphics.BufferObject(128 * 8)
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 3, points_ssbo.id)

    return shader_program, voronoi_diagram_image, points_ssbo