#version 330 core

in vec2 vert;
in vec2 in_text;
out vec2 fragUV;

void main() {
    fragUV = in_text;
    gl_Position = vec4(vert, 0.0, 1.0);
}