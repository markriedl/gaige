package dk.itu.mario.scene;

import java.awt.Graphics;
import java.awt.event.MouseEvent;


import dk.itu.mario.engine.sonar.SonarSoundEngine;
import dk.itu.mario.engine.sonar.SoundListener;


public abstract class Scene implements SoundListener
{
    public SonarSoundEngine sound;
    public static boolean[] keys = new boolean[16];
    
	public static final int COLOR_BLACK = 0;
	public static final int COLOR_RED = 1;
	public static final int COLOR_GREEN = 2;
	public static final int COLOR_BLUE = 3;
	public static final int COLOR_YELLOW = 4;
	public static final int COLOR_PURPLE = 5;
	public static final int COLOR_LIGHTBLUE = 6;
	public static final int COLOR_WHITE = 7;

    public void toggleKey(int key, boolean isPressed)
    {
        keys[key] = isPressed;
    }

    public final void setSound(SonarSoundEngine sound)
    {
        sound.setListener(this);
        this.sound = sound;
    }
    
    public abstract void mouseClicked(MouseEvent me);

    public abstract void init();

    public abstract void tick();

    public abstract void render(Graphics og, float alpha);
}