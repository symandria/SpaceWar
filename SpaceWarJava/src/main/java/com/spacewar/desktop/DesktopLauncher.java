package com.spacewar.desktop;

import com.badlogic.gdx.backends.lwjgl3.Lwjgl3Application;
import com.badlogic.gdx.backends.lwjgl3.Lwjgl3ApplicationConfiguration;
import com.spacewar.core.SpaceWarGame;

/**
 * Desktop launcher for the SpaceWar game.
 * This class sets up the window configuration and starts the game.
 */
public class DesktopLauncher {
    public static void main(String[] args) {
        // Configure the application
        Lwjgl3ApplicationConfiguration config = new Lwjgl3ApplicationConfiguration();
        config.setTitle("SpaceWar");
        config.setWindowedMode(800, 800);
        config.setResizable(false);
        
        // Create and start the application
        new Lwjgl3Application(new SpaceWarGame(), config);
    }
} 