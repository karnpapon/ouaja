#version 460 core
layout(local_size_x = 8, local_size_y = 4, local_size_z = 1) in;
layout(rgba32f, binding = 0) uniform image2D screen;
void main()
{
    vec4 pixel = vec4(1.0, 0.0, 0.0, 1.0);
    ivec2 pixel_coords = ivec2(gl_GlobalInvocationID.xy);

    imageStore(screen, pixel_coords, pixel);
}