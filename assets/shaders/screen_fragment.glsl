#version 330 core

in vec2 fragUV;
out vec4 FragColor;

uniform sampler2D u_dither_tex;
uniform sampler2D u_color_tex;
uniform sampler2D u_screen_tex;

uniform int u_bit_depth;
uniform float u_contrast;
uniform float u_offset;
uniform float u_dither_size;

void main()
{
    // // Pixelate screen sample
    vec2 screen_size = vec2(textureSize(u_screen_tex, 0)) / u_dither_size;
    vec2 screen_sample_uv = floor(fragUV * screen_size) / screen_size;
    vec3 screen_col = texture(u_screen_tex, screen_sample_uv).rgb;

    // Calculate luminance
    float lum = dot(screen_col, vec3(0.299, 0.587, 0.114));

    // Adjust contrast and offset
    lum = (lum - 0.5 + u_offset) * u_contrast + 0.5;
    lum = clamp(lum, 0.0, 1.0);

    // // Reduce bit depth
    float bits = float(u_bit_depth);
    lum = floor(lum * bits) / bits;

    // // Palette banding
    ivec2 col_size = textureSize(u_color_tex, 0);
    col_size /= col_size.y;
    float col_x = float(col_size.x) - 1.0;
    float col_texel_size = 1.0 / col_x;

    lum = max(lum - 0.00001, 0.0);
    float lum_lower = floor(lum * col_x) * col_texel_size;
    float lum_upper = (floor(lum * col_x) + 1.0) * col_texel_size;
    float lum_scaled = lum * col_x - floor(lum * col_x);

    // // Dither threshold lookup
    ivec2 noise_size = textureSize(u_dither_tex, 0);
    vec2 inv_noise_size = 1.0 / vec2(noise_size);
    vec2 noise_uv = fragUV * inv_noise_size * vec2(screen_size);
    float threshold = texture(u_dither_tex, noise_uv).r;
    threshold = threshold * 0.99 + 0.005;

    float ramp_val = lum_scaled < threshold ? 0.0 : 1.0;
    float col_sample = mix(lum_lower, lum_upper, ramp_val);
    // vec3 final_col = texture(u_color_tex, vec2(col_sample, 0.5)).rgb;

    vec2 col_tex_size = vec2(textureSize(u_color_tex, 0));
    vec2 palette_uv = vec2(col_sample, (0.5 / col_tex_size.y));
    vec3 final_col = texture(u_color_tex, palette_uv).rgb;

    FragColor = vec4(final_col, 1.0);
}