package com.spacewar.core;

import com.badlogic.gdx.Game;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.graphics.GL20;

/**
 * Main game class that serves as the entry point for the SpaceWar game.
 */
public class SpaceWarGame extends Game {
    
    @Override
    public void create() {
        // Set the clear color to black
        Gdx.gl.glClearColor(0, 0, 0, 1);
    }
    
    @Override
    public void render() {
        // Clear the screen
        Gdx.gl.glClear(GL20.GL_COLOR_BUFFER_BIT);
        
        // Call the super method to render the active screen
        super.render();
    }
    
    @Override
    public void dispose() {
        // Clean up resources
        super.dispose();
    }
} 