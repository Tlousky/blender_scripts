# This script, which can be used via a python controller in the game engine
# Allows you to tkae a screenshot which represents the game engine render precisely,
# and allows utilizing its ability to effectively render out GLSL effects and shaders
# Very quickly

import bpy,bge

def main():
    # Render frame
    bge.render.makeScreenshot(bpy.context.scene.render.frame_path())
    # Advance to next frame
    bpy.context.scene.frame_set(bpy.context.scene.frame_current + 1)
main()
