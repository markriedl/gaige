package dk.itu.mario.engine;

import java.awt.AlphaComposite;
import java.awt.Graphics2D;
import java.awt.GraphicsConfiguration;
import java.awt.Image;
import java.awt.Transparency;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;
import javax.sound.midi.MidiSystem;
import javax.sound.midi.Sequence;
import javax.sound.midi.Sequencer;


import dk.itu.mario.engine.sonar.SonarSoundEngine;
import dk.itu.mario.engine.sonar.sample.SonarSample;
import java.io.InputStream;
import dk.itu.mario.res.ResourcesManager;


public class Art
{
    public static final int SAMPLE_BREAK_BLOCK = 0;
    public static final int SAMPLE_GET_COIN = 1;
    public static final int SAMPLE_MARIO_JUMP = 2;
    public static final int SAMPLE_MARIO_STOMP = 3;
    public static final int SAMPLE_MARIO_KICK = 4;
    public static final int SAMPLE_MARIO_POWER_UP = 5;
    public static final int SAMPLE_MARIO_POWER_DOWN = 6;
    public static final int SAMPLE_MARIO_DEATH = 7;
    public static final int SAMPLE_ITEM_SPROUT = 8;
    public static final int SAMPLE_CANNON_FIRE = 9;
    public static final int SAMPLE_SHELL_BUMP = 10;
    public static final int SAMPLE_LEVEL_EXIT = 11;
    public static final int SAMPLE_MARIO_1UP = 12;
    public static final int SAMPLE_MARIO_FIREBALL = 13;

    public static Image[][] mario;
    public static Image[][] smallMario;
    public static Image[][] fireMario;
    public static Image[][] enemies;
    public static Image[][] items;
    public static Image[][] level;
    public static Image[][] particles;
    public static Image[][] font;
    public static Image[][] bg;
    public static Image[][] map;
    public static Image[][] endScene;
    public static Image[][] gameOver;
    public static Image logo;
    public static Image titleScreen;
    public static Image keys, abkey;

    public static SonarSample[] samples = new SonarSample[100];

    private static Sequence[] songs = new Sequence[10];
    private static Sequencer sequencer;

    public static boolean mute = true;
    private static final String PREFIX="res";


    public static void init(GraphicsConfiguration gc, SonarSoundEngine sound)
    {
        try
        {
            mario = cutImage(gc, PREFIX+"/mariosheet.png", 32, 32);
            smallMario = cutImage(gc, PREFIX+"/smallmariosheet.png", 16, 16);
            fireMario = cutImage(gc, PREFIX+"/firemariosheet.png", 32, 32);
            enemies = cutImage(gc, PREFIX+"/enemysheet.png", 16, 32);
            items = cutImage(gc,PREFIX+ "/itemsheet.png", 16, 16);
            level = cutImage(gc, PREFIX+"/mapsheet.png", 16, 16);
            map = cutImage(gc, PREFIX+"/worldmap.png", 16, 16);
            particles = cutImage(gc, PREFIX+"/particlesheet.png", 8, 8);
            bg = cutImage(gc,PREFIX+ "/bgsheet.png", 32, 32);
            logo = getImage(gc, PREFIX+"/logo.gif");
            titleScreen = getImage(gc, PREFIX+"/title.gif");
            font = cutImage(gc, PREFIX+"/font.gif", 8, 8);
            endScene = cutImage(gc,PREFIX+ "/endscene.gif", 96, 96);
            gameOver = cutImage(gc, PREFIX+"/gameovergost.gif", 96, 64);
            keys = getImage(gc, PREFIX+"/keys.png");
            abkey = getImage(gc, PREFIX+"/abkey.png");

            if (sound != null)
            {
                samples[SAMPLE_BREAK_BLOCK] = sound.loadSample(PREFIX+"/snd/breakblock.wav");
                samples[SAMPLE_GET_COIN] = sound.loadSample(PREFIX+"/snd/coin.wav");
                samples[SAMPLE_MARIO_JUMP] = sound.loadSample(PREFIX+"/snd/jump.wav");
                samples[SAMPLE_MARIO_STOMP] = sound.loadSample(PREFIX+"/snd/stomp.wav");
                samples[SAMPLE_MARIO_KICK] = sound.loadSample(PREFIX+"/snd/kick.wav");
                samples[SAMPLE_MARIO_POWER_UP] = sound.loadSample(PREFIX+"/snd/powerup.wav");
                samples[SAMPLE_MARIO_POWER_DOWN] = sound.loadSample(PREFIX+"/snd/powerdown.wav");
                samples[SAMPLE_MARIO_DEATH] = sound.loadSample(PREFIX+"/snd/death.wav");
                samples[SAMPLE_ITEM_SPROUT] = sound.loadSample(PREFIX+"/snd/sprout.wav");
                samples[SAMPLE_CANNON_FIRE] = sound.loadSample(PREFIX+"/snd/cannon.wav");
                samples[SAMPLE_SHELL_BUMP] = sound.loadSample(PREFIX+"/snd/bump.wav");
                samples[SAMPLE_LEVEL_EXIT] = sound.loadSample(PREFIX+"/snd/exit.wav");
                samples[SAMPLE_MARIO_1UP] = sound.loadSample(PREFIX+"/snd/1-up.wav");
                samples[SAMPLE_MARIO_FIREBALL] = sound.loadSample(PREFIX+"/snd/fireball.wav");
            }
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }

        try
        {
            sequencer = MidiSystem.getSequencer();
            sequencer.open();
            songs[0] = MidiSystem.getSequence(ResourcesManager.class.getResourceAsStream(PREFIX+"/mus/smb3map1.mid"));
            songs[1] = MidiSystem.getSequence(ResourcesManager.class.getResourceAsStream(PREFIX+"/mus/smwovr1.mid"));
            songs[2] = MidiSystem.getSequence(ResourcesManager.class.getResourceAsStream(PREFIX+"/mus/smb3undr.mid"));
            songs[3] = MidiSystem.getSequence(ResourcesManager.class.getResourceAsStream(PREFIX+"/mus/smwfortress.mid"));
            songs[4] = MidiSystem.getSequence(ResourcesManager.class.getResourceAsStream(PREFIX+"/mus/smwtitle.mid"));
        }
        catch (Exception e)
        {
            sequencer = null;
            e.printStackTrace();
        }
    }

    private static Image getImage(GraphicsConfiguration gc, String imageName) throws IOException
    {
        InputStream p=ResourcesManager.class.getResourceAsStream(imageName);
        BufferedImage source = ImageIO.read(p);
        Image image = gc.createCompatibleImage(source.getWidth(), source.getHeight(), Transparency.BITMASK);
        Graphics2D g = (Graphics2D) image.getGraphics();
        g.setComposite(AlphaComposite.Src);
        g.drawImage(source, 0, 0, null);
        g.dispose();
        return image;
    }

    private static Image[][] cutImage(GraphicsConfiguration gc, String imageName, int xSize, int ySize) throws IOException
    {
        Image source = getImage(gc, imageName);
        Image[][] images = new Image[source.getWidth(null) / xSize][source.getHeight(null) / ySize];
        for (int x = 0; x < source.getWidth(null) / xSize; x++)
        {
            for (int y = 0; y < source.getHeight(null) / ySize; y++)
            {
                Image image = gc.createCompatibleImage(xSize, ySize, Transparency.BITMASK);
                Graphics2D g = (Graphics2D) image.getGraphics();
                g.setComposite(AlphaComposite.Src);
                g.drawImage(source, -x * xSize, -y * ySize, null);
                g.dispose();
                images[x][y] = image;
            }
        }

        return images;
    }

    public static void startMusic(int song)
    {
    	if(!mute){
	        stopMusic();
	        if (sequencer != null)
	        {
	            try
	            {
	                sequencer.open();
	                sequencer.setSequence((Sequence)null);
	                sequencer.setSequence(songs[song]);
                        int i = Sequencer.LOOP_CONTINUOUSLY;
	                sequencer.setLoopCount(Sequencer.LOOP_CONTINUOUSLY);
	                sequencer.start();
	            }
	            catch (Exception e)
	            {
	            }
	        }
        }
    }

    public static void stopMusic()
    {
        if (sequencer != null)
        {
            try
            {
                sequencer.stop();
                sequencer.close();
            }
            catch (Exception e)
            {
            }
        }
    }
}
