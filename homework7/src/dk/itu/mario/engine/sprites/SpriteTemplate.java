package dk.itu.mario.engine.sprites;

import dk.itu.mario.scene.LevelScene;

public class SpriteTemplate
{
	public static final int RED_TURTLE		= 0;
	public static final int GREEN_TURTLE	= 1;
	public static final int GOOMPA			= 2;
	public static final int ARMORED_TURTLE	= 3;
	public static final int JUMP_FLOWER		= 4;
	public static final int CANNON_BALL		= 5;
	public static final int CHOMP_FLOWER	= 6;

	public static int enemiesSpawned = 0;
	public static int enemiesMax = 1000;

	public boolean hasSpawned = false;

    public int lastVisibleTick = -1;
    public Sprite sprite;
    public boolean isDead = false;
    private boolean winged;

    public int type;
    public int direction = 1;

    public SpriteTemplate(int type, boolean winged)
    {
        this.type = type;
        this.winged = winged;
    }

    public void spawn(LevelScene world, int x, int y, int dir)
    {
        if (isDead || enemiesSpawned >= enemiesMax) return;

        if (type==Enemy.ENEMY_FLOWER)
        {
            sprite = new FlowerEnemy(world, x*16+15, y*16+24);
        }
        else
        {
            sprite = new Enemy(world, x*16+8, y*16+15, dir, type, winged);
        }

        //correct for flipping
        if(direction == -1){
        	sprite.x -= 14;
        }

        sprite.spriteTemplate = this;
        world.addSprite(sprite);

        if(!hasSpawned)
        	enemiesSpawned++;

        hasSpawned = true;
    }
}
