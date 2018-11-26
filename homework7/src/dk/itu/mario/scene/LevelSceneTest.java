package dk.itu.mario.scene;
import java.awt.GraphicsConfiguration;
import java.io.DataInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Random;


import dk.itu.mario.engine.level.BgLevelGenerator;
import dk.itu.mario.MarioInterface.GamePlay;
import dk.itu.mario.engine.sonar.FixedSoundSource;
import dk.itu.mario.engine.sprites.CoinAnim;
import dk.itu.mario.engine.sprites.FireFlower;
import dk.itu.mario.engine.sprites.Mario;
import dk.itu.mario.engine.sprites.Mushroom;
import dk.itu.mario.engine.sprites.Particle;
import dk.itu.mario.engine.sprites.Sprite;
import dk.itu.mario.engine.util.FileHandler;

import dk.itu.mario.engine.Art;
import dk.itu.mario.engine.BgRenderer;
import dk.itu.mario.engine.DataRecorder;
import dk.itu.mario.engine.LevelRenderer;
import dk.itu.mario.engine.MarioComponent;
import dk.itu.mario.engine.level.Level;
import dk.itu.mario.engine.level.generator.MyLevelGenerator;
import dk.itu.mario.engine.level.MyLevel;
import dk.itu.mario.engine.Play;
import dk.itu.mario.res.ResourcesManager;

//Test
import dk.itu.mario.engine.PlayerProfile;
import dk.itu.mario.engine.Scrooge;
import dk.itu.mario.engine.Killer;
import dk.itu.mario.engine.KillerCollector;
import dk.itu.mario.engine.Jumper;

public class LevelSceneTest extends LevelScene{

			ArrayList<Double> switchPoints;
			private double thresshold; //how large the distance from point to mario should be before switching
			private int point = -1;
			private int []checkPoints;
			private boolean isCustom;
			private String playerProfile = "";


			public LevelSceneTest(GraphicsConfiguration graphicsConfiguration,
					MarioComponent renderer, long seed, int levelDifficulty, int type,String playerProfile){
				super(graphicsConfiguration,renderer,seed,levelDifficulty,type);
				this.isCustom = true;
				this.playerProfile = playerProfile;
			}

			public void init() {
		        try
		        {
		            Level.loadBehaviors(new DataInputStream(ResourcesManager.class.getResourceAsStream("res/tiles.dat")));
		        }
		        catch (IOException e)
		        {
		            e.printStackTrace();
		            System.exit(0);
		        }

		        if(level==null)
		        	if(isCustom){

		        		MyLevelGenerator clg = new MyLevelGenerator();

		        		//Select the profile to use. Default to scrooge
		        		PlayerProfile p = new Scrooge();
		        		if (playerProfile.equals("Killer") ){
		        			p = new Killer();
		        		}
		        		else if (playerProfile.equals("Jumper") ){
		        			p = new Jumper();
		        		}
		        		else if(playerProfile.equals("KillerCollector")){
		        			p = new KillerCollector();
		        		}
						

		        		currentLevel = clg.generateLevel(p);

		        		if (recorder==null){
				            recorder = new DataRecorder(this,level,keys);
				        }
		        		
		        		//You can use the following commands if you want to benefit from
		        		//	the interface containing detailed information
		                
		              }
			        	

		        try {
					 level = currentLevel.clone();
				} catch (CloneNotSupportedException e) {
					e.printStackTrace();
				}

		        //level is always overground
		        Art.startMusic(1);

		        paused = false;
		        Sprite.spriteContext = this;
		        sprites.clear();

		        layer = new LevelRenderer(level, graphicsConfiguration, 320, 240);
		        for (int i = 0; i < 2; i++)
		        {
		            int scrollSpeed = 4 >> i;
		            int w = ((level.getWidth() * 16) - 320) / scrollSpeed + 320;
		            int h = ((level.getHeight() * 16) - 240) / scrollSpeed + 240;
		            Level bgLevel = BgLevelGenerator.createLevel(w / 32 + 1, h / 32 + 1, i == 0, levelType);
		            bgLayer[i] = new BgRenderer(bgLevel, graphicsConfiguration, 320, 240, scrollSpeed);
		        }

		        double oldX = 0;
		        if(mario!=null)
		        	oldX = mario.x;

		        mario = new Mario(this);
		        sprites.add(mario);
		        startTime = 1;

		        timeLeft = 200*15;

		        tick = 0;

		        /*
		         * SETS UP ALL OF THE CHECKPOINTS TO CHECK FOR SWITCHING
		         */
		        switchPoints = new ArrayList<Double>();

		        //first pick a random starting waypoint from among ten positions
		    	int squareSize = 16; //size of one square in pixels
		        int sections = 10;

		    	double startX = 32; //mario start position
		    	double endX = level.getxExit()*squareSize; //position of the end on the level
		    	if(!isCustom && recorder==null)
		    		recorder = new DataRecorder(this,(MyLevel)level,keys);

		        gameStarted = false;
			}



			public void tick(){
				super.tick();

				if(recorder != null && !gameStarted){
					recorder.startLittleRecord();
					recorder.startTime();
					gameStarted = true;
				}
				if(recorder != null)
				recorder.tickRecord();
			}

			public void winActions(){				
				marioComponent.win();
			}

			//HERE IS WHAT DETERMINES WHAT HAPPENS WHEN MARIO DIES
			public void deathActions(){
				if(Mario.lives <=0){//has no more lives
					if(recorder != null)
					recorder.fillGamePlayMetrics((MyLevel)level);
					marioComponent.lose();
				}
				else // mario still has lives to play :)--> have a new beginning
					reset();
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

			private int randomNumber(int low, int high){
				return new Random(new Random().nextLong()).nextInt(high-low)+low;
			}

			private int toBlock(float n){
				return (int)(n/16);
			}

			private int toBlock(double n){
				return (int)(n/16);
			}

			private float toReal(int b){
				return b*16;
			}



}
