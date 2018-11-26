package dk.itu.mario.scene;

import java.awt.Color;
import java.awt.Graphics;
import java.awt.GraphicsConfiguration;
import java.awt.Image;
import java.awt.event.MouseEvent;
import java.io.*;
import java.text.DecimalFormat;
import java.util.*;


import dk.itu.mario.engine.Art;
import dk.itu.mario.engine.BgRenderer;
import dk.itu.mario.engine.DataRecorder;
import dk.itu.mario.engine.LevelRenderer;
import dk.itu.mario.engine.MarioComponent;
import dk.itu.mario.engine.level.Level;
import dk.itu.mario.engine.level.MyLevel;

import dk.itu.mario.engine.sonar.FixedSoundSource;
import dk.itu.mario.engine.sprites.*;
import dk.itu.mario.engine.sprites.BulletBill;
import dk.itu.mario.engine.sprites.CoinAnim;
import dk.itu.mario.engine.sprites.FireFlower;
import dk.itu.mario.engine.sprites.Fireball;
import dk.itu.mario.engine.sprites.Mario;
import dk.itu.mario.engine.sprites.Mushroom;
import dk.itu.mario.engine.sprites.Particle;
import dk.itu.mario.engine.sprites.Shell;
import dk.itu.mario.engine.sprites.Sparkle;
import dk.itu.mario.engine.sprites.Sprite;
import dk.itu.mario.engine.sprites.SpriteContext;
import dk.itu.mario.engine.sprites.SpriteTemplate;


public class LevelScene extends Scene implements SpriteContext
{
    protected List<Sprite> sprites = new ArrayList<Sprite>();
    protected List<Sprite> spritesToAdd = new ArrayList<Sprite>();
    protected List<Sprite> spritesToRemove = new ArrayList<Sprite>();

    public Level level;
//    public Level levelTemp;
    public Mario mario;
    public float xCam, yCam, xCamO, yCamO;
    public static Image tmpImage;
    protected int tick;

    protected LevelRenderer layer;
    protected BgRenderer[] bgLayer = new BgRenderer[2];
    protected Level currentLevel;
    protected GraphicsConfiguration graphicsConfiguration;

    public boolean paused = false;
    public int startTime = 0;
    public int timeLeft;

    //    private Recorder recorder = new Recorder();
    //    private Replayer replayer = null;

    protected long levelSeed;
    protected MarioComponent marioComponent;
    protected int levelType;
    protected int levelDifficulty;

    public static DataRecorder recorder;

    public boolean gameStarted;

    public static boolean bothPlayed = false;

    private int []xPositionsArrow;
    private int []yPositionsArrow;
    private int widthArrow,heightArrow,tipWidthArrow;
    private int xArrow,yArrow;

    public LevelScene(GraphicsConfiguration graphicsConfiguration, MarioComponent renderer, long seed, int levelDifficulty, int type)
    {
        this.graphicsConfiguration = graphicsConfiguration;
        this.levelSeed = seed;
        this.marioComponent = renderer;
        this.levelDifficulty = levelDifficulty;
        this.levelType = type;

        widthArrow = 25;
    	tipWidthArrow = 10;
    	heightArrow = 20;

    	xArrow = 160;
    	yArrow = 40;

    	xPositionsArrow = new int[]{xArrow+-widthArrow/2,xArrow+widthArrow/2-tipWidthArrow,xArrow+widthArrow/2-tipWidthArrow,xArrow+widthArrow/2,xArrow+widthArrow/2-tipWidthArrow,xArrow+widthArrow/2-tipWidthArrow,xArrow+-widthArrow/2};
    	yPositionsArrow = new int[]{yArrow+-heightArrow/4,yArrow+-heightArrow/4,yArrow+-heightArrow/2,yArrow+0,yArrow+heightArrow/2,yArrow+heightArrow/4,yArrow+heightArrow/4};
    }

    public void init()
    {

    }

    public int getWidth() {
        // TODO Auto-generated method stub
        return level.getWidth();
    }
    public int getHeight() {
        // TODO Auto-generated method stub
        return level.getHeight();
    }

    public int fireballsOnScreen = 0;

    List<Shell> shellsToCheck = new ArrayList<Shell>();

    public void checkShellCollide(Shell shell)
    {
        shellsToCheck.add(shell);
    }

    List<Fireball> fireballsToCheck = new ArrayList<Fireball>();

    public void checkFireballCollide(Fireball fireball)
    {
        fireballsToCheck.add(fireball);
    }

    public void tick(){
        timeLeft--;

        if( widthArrow < 0){
        	widthArrow*=-1;
        	tipWidthArrow*=-1;

        	xPositionsArrow = new int[]{xArrow+-widthArrow/2,xArrow+widthArrow/2-tipWidthArrow,xArrow+widthArrow/2-tipWidthArrow,xArrow+widthArrow/2,xArrow+widthArrow/2-tipWidthArrow,xArrow+widthArrow/2-tipWidthArrow,xArrow+-widthArrow/2};
        	yPositionsArrow = new int[]{yArrow+-heightArrow/4,yArrow+-heightArrow/4,yArrow+-heightArrow/2,yArrow+0,yArrow+heightArrow/2,yArrow+heightArrow/4,yArrow+heightArrow/4};

        }

        if (timeLeft==0)
        {
            mario.dieTime();
        }

        xCamO = xCam;
        yCamO = yCam;

        if (startTime > 0)
        {
            startTime++;
        }


        float targetXCam = 0;

        if(mario!=null) targetXCam=mario.x - 160;

        xCam = targetXCam;

        if (xCam < 0) xCam = 0;
        if (xCam > level.getWidth() * 16 - 320) xCam = level.getWidth() * 16 - 320;

        /*      if (recorder != null)
         {
         recorder.addTick(mario.getKeyMask());
         }

         if (replayer!=null)
         {
         mario.setKeys(replayer.nextTick());
         }*/

        fireballsOnScreen = 0;

        for (Sprite sprite : sprites)
        {
            if (sprite != mario)
            {
                float xd = sprite.x - xCam;
                float yd = sprite.y - yCam;
                if (xd < -64 || xd > 320 + 64 || yd < -64 || yd > 240 + 64)
                {
                    removeSprite(sprite);
                }
                else
                {
                    if (sprite instanceof Fireball)
                    {
                        fireballsOnScreen++;
                    }
                }
            }
        }

        if (paused)
        {
            for (Sprite sprite : sprites)
            {
                if (sprite == mario)
                {
                    sprite.tick();
                }
                else
                {
                    sprite.tickNoMove();
                }
            }
        }
        else if(mario!=null)
        {

            tick++;
            level.tick();

            boolean hasShotCannon = false;
            int xCannon = 0;

            for (int x = (int) xCam / 16 - 1; x <= (int) (xCam + layer.width) / 16 + 1; x++)
                for (int y = (int) yCam / 16 - 1; y <= (int) (yCam + layer.height) / 16 + 1; y++)
                {
                    int dir = 0;

                    if (x * 16 + 8 > mario.x + 16) dir = -1;
                    if (x * 16 + 8 < mario.x - 16) dir = 1;

                    SpriteTemplate st = level.getSpriteTemplate(x, y);

                    if (st != null)
                    {
                        if (st.lastVisibleTick != tick - 1)
                        {
                            if (st.sprite == null || !sprites.contains(st.sprite))
                            {
                                st.spawn(this, x, y, dir);

							}
                        }

                        st.lastVisibleTick = tick;
                    }

                    if (dir != 0)
                    {
                        byte b = level.getBlock(x, y);
                        if (((Level.TILE_BEHAVIORS[b & 0xff]) & Level.BIT_ANIMATED) > 0)
                        {
                            if ((b % 16) / 4 == 3 && b / 16 == 0)
                            {
                                if ((tick - x * 2) % 100 == 0)
                                {
                                    xCannon = x;
                                    for (int i = 0; i < 8; i++)
                                    {
                                        addSprite(new Sparkle(x * 16 + 8, y * 16 + (int) (Math.random() * 16), (float) Math.random() * dir, 0, 0, 1, 5));
                                    }
                                    addSprite(new BulletBill(this, x * 16 + 8 + dir * 8, y * 16 + 15, dir));
                                    hasShotCannon = true;
                                }
                            }
                        }
                    }
                }

            if (hasShotCannon)
            {
                sound.play(Art.samples[Art.SAMPLE_CANNON_FIRE], new FixedSoundSource(xCannon * 16, yCam + 120), 1, 1, 1);
            }

            for (Sprite sprite : sprites)
            {
                sprite.tick();
            }

            for (Sprite sprite : sprites)
            {
                sprite.collideCheck();
            }

            for (Shell shell : shellsToCheck)
            {
                for (Sprite sprite : sprites)
                {
                    if (sprite != shell && !shell.dead)
                    {
                        if (sprite.shellCollideCheck(shell))
                        {
                            if (mario.carried == shell && !shell.dead)
                            {
                                mario.carried = null;
                                shell.die();
                            }
                        }
                    }
                }
            }
            shellsToCheck.clear();

            for (Fireball fireball : fireballsToCheck)
            {
                for (Sprite sprite : sprites)
                {
                    if (sprite != fireball && !fireball.dead)
                    {
                        if (sprite.fireballCollideCheck(fireball))
                        {
                            fireball.die();
                        }
                    }
                }
            }
            fireballsToCheck.clear();
        }

        sprites.addAll(0, spritesToAdd);
        sprites.removeAll(spritesToRemove);
        spritesToAdd.clear();
        spritesToRemove.clear();

    }

    private DecimalFormat df = new DecimalFormat("00");
    private DecimalFormat df2 = new DecimalFormat("000");

    public void render(Graphics g, float alpha)
    {
        int xCam = 0;
        if (mario!=null) xCam=(int) (mario.xOld + (mario.x - mario.xOld) * alpha) - 160;
        int yCam =0;
        if (mario!=null) yCam = (int) (mario.yOld + (mario.y - mario.yOld) * alpha) - 120;
        //int xCam = (int) (xCamO + (this.xCam - xCamO) * alpha);
        //        int yCam = (int) (yCamO + (this.yCam - yCamO) * alpha);
        if (xCam < 0) xCam = 0;
        if (yCam < 0) yCam = 0;
        if (xCam > level.getWidth() * 16 - 320) xCam = level.getWidth() * 16 - 320;
        if (yCam > level.getHeight() * 16 - 240) yCam = level.getHeight() * 16 - 240;

        //      g.drawImage(Art.background, 0, 0, null);

        for (int i = 0; i < 2; i++)
        {
            bgLayer[i].setCam(xCam, yCam);
            bgLayer[i].render(g, tick, alpha);
        }

        g.translate(-xCam, -yCam);
        for (Sprite sprite : sprites)
        {
            if (sprite.layer == 0) sprite.render(g, alpha);
        }
        g.translate(xCam, yCam);
        
        ////////////THIS RENDERS THE LEVEL
        layer.setCam(xCam, yCam);
        layer.render(g, tick, paused?0:alpha);
        if (mario!=null) layer.renderExit0(g, tick, paused?0:alpha, mario.winTime==0);
        ////////////END OF LEVEL RENDER


        ////////////RENDERS SPRITES
        g.translate(-xCam, -yCam);
        for (Sprite sprite : sprites)
        {
            if (sprite.layer == 1) sprite.render(g, alpha);
        }
        g.translate(xCam, yCam);
        g.setColor(Color.BLACK);
        layer.renderExit1(g, tick, paused?0:alpha);
        ////////////END OF SPRITE RENDERING

        drawStringDropShadow(g, "MARIO " + df.format(Mario.lives), 0, 0, 7);
//        drawStringDropShadow(g, "00000000", 0, 1, 7);

        drawStringDropShadow(g, "COIN", 14, 0, 7);
        drawStringDropShadow(g, " "+df.format(Mario.coins), 14, 1, 7);

        drawStringDropShadow(g, "WORLD", 24, 0, 7);
        drawStringDropShadow(g, " "+Mario.levelString, 24, 1, 7);

        drawStringDropShadow(g, "TIME", 35, 0, 7);
        int time = (timeLeft+15-1)/15;
        if (time<0) time = 0;
        drawStringDropShadow(g, " "+df2.format(time), 35, 1, 7);

        renderDirectionArrow(g);


        if (startTime > 0)
        {
            float t = startTime + alpha - 2;
            t = t * t * 0.6f;
            renderBlackout(g, 160, 120, (int) (t));
        }
//        mario.x>level.xExit*16
        if (mario!=null && mario.winTime > 0)
        {
            float t = mario.winTime + alpha;
            t = t * t * 0.2f;

            if (t > 0){
                if(recorder != null){
                	recorder.stopRecord();
                	recorder.levelWon();
//                	recorder.printAll();
                }

            }

            if (t > 900)
            {
                winActions();
                return;


                //              replayer = new Replayer(recorder.getBytes());
//                init();
            }

            renderBlackout(g, (int) (mario.xDeathPos - xCam), (int) (mario.yDeathPos - yCam), (int) (320 - t));
        }

        if (mario!=null && mario.deathTime > 0)
        {
        	g.setColor(Color.BLACK);
            float t = mario.deathTime + alpha;
            t = t * t * 0.4f;

            if(t > 0 && Mario.lives <= 0){
                if(recorder != null){
                	recorder.stopRecord();
                }
            }

            if (t > 1800)
            {
            	Mario.lives--;
            	deathActions();
           }

            renderBlackout(g, (int) (mario.xDeathPos - xCam), (int) (mario.yDeathPos - yCam), (int) (320 - t));
        }
    }

    public void winActions(){

    }

    public void deathActions(){

    }

    public void SpriteRender(Graphics og, float alpha){
        for (Sprite sprite : sprites){
            sprite.specialRender(og, alpha);
        }
    }

    protected void reset(){
		paused = false;
        Sprite.spriteContext = this;
        sprites.clear();

        try {
			level = currentLevel.clone();
		} catch (CloneNotSupportedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
        level.resetSpriteTemplate();

        layer = new LevelRenderer(level, graphicsConfiguration, 320, 240);

        double oldX = 0;

        if(mario!=null){
        	oldX = mario.x;
        }

        mario = new Mario(this);
        sprites.add(mario);
        startTime = 1;

        timeLeft = 200*15;
        Art.startMusic(1);
        tick = 0;
        if (recorder==null){
            recorder = new DataRecorder(this,level,keys);
        }
        recorder.detailedLog += "NEWLEVELSTART\n";
        gameStarted = false;
	}

    private void renderDirectionArrow(Graphics g){
    	if(widthArrow<0)
    		g.setColor(new Color(0,0,255,150));
    	else
    		g.setColor(new Color(255,0,0,150));

    	g.fillPolygon(xPositionsArrow,yPositionsArrow,Math.min(xPositionsArrow.length,yPositionsArrow.length));
    	g.setColor(new Color(0,0,0,255));
    	g.drawPolygon(xPositionsArrow,yPositionsArrow,Math.min(xPositionsArrow.length,yPositionsArrow.length));
    }

    private void drawStringDropShadow(Graphics g, String text, int x, int y, int c)
    {
        drawString(g, text, x*8+5, y*8+5, 0);
        drawString(g, text, x*8+4, y*8+4, c);
    }

    private void drawString(Graphics g, String text, int x, int y, int c)
    {
        char[] ch = text.toCharArray();
        for (int i = 0; i < ch.length; i++)
        {
            g.drawImage(Art.font[ch[i] - 32][c], x + i * 8, y, null);
        }
    }

    float decrease = (float)0.03;
    float factor = 0;
    boolean in = true;
    String flipText = "FLIP! MOVE THE OTHER WAY!";

//    protected void renderFlip(Graphics g){
//
//        if(level.startFlipping){
//            if(in){
//            	factor += decrease;
//            	if(factor>=1){
//            		in = false;
//            		level.canFlip = true;
//            	}
//            }
//            else{
//
//            	factor -= decrease;
//
//            	if(factor<=0){
//            		in = true;
//            		level.startFlipping = false;
//            	}
//            }
//
//            int width = 320;
//            int height = 240;
//            int overlap = 20;
//
//        	g.setColor(Color.BLACK);
//        	g.fillRect(0,0,(int)((width/2)*factor) + overlap, height);
//
//        	g.setColor(Color.BLACK);
//        	g.fillRect(width - overlap -(int)((width/2)*factor),0,(int)((width/2)*factor) + overlap,height);
//
//        	//draw a box behind the string so you can see it
//        	int padding = 3;
//
//        	g.setColor(new Color(0,0,0,100));
//        	g.fillRect(width/2-flipText.length()*8/2-padding,height/2-padding,flipText.length()*8 + 2*padding,10 + 2*padding);
//        	drawString(g,flipText, width/2-flipText.length()*8/2+2, height/2+2, 0);
//        	drawString(g,flipText,width/2-flipText.length()*8/2,height/2,2);
//
//        }
//    }

    private void renderBlackout(Graphics g, int x, int y, int radius)
    {
        if (radius > 320) return;

        int[] xp = new int[20];
        int[] yp = new int[20];
        for (int i = 0; i < 16; i++)
        {
            xp[i] = x + (int) (Math.cos(i * Math.PI / 15) * radius);
            yp[i] = y + (int) (Math.sin(i * Math.PI / 15) * radius);
        }
        xp[16] = 320;
        yp[16] = y;
        xp[17] = 320;
        yp[17] = 240;
        xp[18] = 0;
        yp[18] = 240;
        xp[19] = 0;
        yp[19] = y;
        g.fillPolygon(xp, yp, xp.length);

        for (int i = 0; i < 16; i++)
        {
            xp[i] = x - (int) (Math.cos(i * Math.PI / 15) * radius);
            yp[i] = y - (int) (Math.sin(i * Math.PI / 15) * radius);
        }
        xp[16] = 320;
        yp[16] = y;
        xp[17] = 320;
        yp[17] = 0;
        xp[18] = 0;
        yp[18] = 0;
        xp[19] = 0;
        yp[19] = y;

        g.fillPolygon(xp, yp, xp.length);
    }


    public void addSprite(Sprite sprite)
    {
        spritesToAdd.add(sprite);
        sprite.tick();
    }

    public void removeSprite(Sprite sprite)
    {
        spritesToRemove.add(sprite);
    }

    public float getX(float alpha)
    {
        int xCam = (int) (mario.xOld + (mario.x - mario.xOld) * alpha) - 160;
        //        int yCam = (int) (mario.yOld + (mario.y - mario.yOld) * alpha) - 120;
        //int xCam = (int) (xCamO + (this.xCam - xCamO) * alpha);
        //        int yCam = (int) (yCamO + (this.yCam - yCamO) * alpha);
        if (xCam < 0) xCam = 0;
        //        if (yCam < 0) yCam = 0;
        //        if (yCam > 0) yCam = 0;
        return xCam + 160;
    }

    public float getY(float alpha)
    {
        return 0;
    }

    public void bump(int x, int y, boolean canBreakBricks)
    {
        byte block = level.getBlock(x, y);

        if ((Level.TILE_BEHAVIORS[block & 0xff] & Level.BIT_BUMPABLE) > 0)
        {
            bumpInto(x, y - 1);
            level.setBlock(x, y, (byte) 4);

            if (((Level.TILE_BEHAVIORS[block & 0xff]) & Level.BIT_SPECIAL) > 0)
            {
                sound.play(Art.samples[Art.SAMPLE_ITEM_SPROUT], new FixedSoundSource(x * 16 + 8, y * 16 + 8), 1, 1, 1);
                if (!Mario.large)
                {
                    addSprite(new Mushroom(this, x * 16 + 8, y * 16 + 8));
                }
                else
                {
                    addSprite(new FireFlower(this, x * 16 + 8, y * 16 + 8));
                }

                if(recorder != null){
                	recorder.blockPowerDestroyRecord();
                }
            }
            else
            {
            	//TODO should only record hidden coins (in boxes)
            	if(recorder != null){
            		recorder.blockCoinDestroyRecord();
            	}

                Mario.getCoin();
                sound.play(Art.samples[Art.SAMPLE_GET_COIN], new FixedSoundSource(x * 16 + 8, y * 16 + 8), 1, 1, 1);
                addSprite(new CoinAnim(x, y));
            }
        }

        if ((Level.TILE_BEHAVIORS[block & 0xff] & Level.BIT_BREAKABLE) > 0)
        {
            bumpInto(x, y - 1);
            if (canBreakBricks)
            {
            	if(recorder != null){
            		recorder.blockEmptyDestroyRecord();
            	}

                sound.play(Art.samples[Art.SAMPLE_BREAK_BLOCK], new FixedSoundSource(x * 16 + 8, y * 16 + 8), 1, 1, 1);
                level.setBlock(x, y, (byte) 0);
                for (int xx = 0; xx < 2; xx++)
                    for (int yy = 0; yy < 2; yy++)
                        addSprite(new Particle(x * 16 + xx * 8 + 4, y * 16 + yy * 8 + 4, (xx * 2 - 1) * 4, (yy * 2 - 1) * 4 - 8));
            }

        }
    }

    public void bumpInto(int x, int y)
    {
        byte block = level.getBlock(x, y);
        if (((Level.TILE_BEHAVIORS[block & 0xff]) & Level.BIT_PICKUPABLE) > 0)
        {
            Mario.getCoin();
            sound.play(Art.samples[Art.SAMPLE_GET_COIN], new FixedSoundSource(x * 16 + 8, y * 16 + 8), 1, 1, 1);
            level.setBlock(x, y, (byte) 0);
            addSprite(new CoinAnim(x, y + 1));

            //TODO no idea when this happens... maybe remove coin count
            if(recorder != null)
            	recorder.recordCoin();
        }

        for (Sprite sprite : sprites)
        {
            sprite.bumpCheck(x, y);
        }
    }
    public void setLevel(Level level){
    	this.level = level;
    }

	@Override
	public void mouseClicked(MouseEvent me) {
		// TODO Auto-generated method stub

	}
}
