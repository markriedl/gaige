package dk.itu.mario.engine;


import dk.itu.mario.engine.PlayerProfile;
import dk.itu.mario.engine.level.Level;
import dk.itu.mario.engine.sprites.Enemy;

//This player profile wants to be constantly able to kill enemies (wants 1 enemy per every 4 blocks)
public class Killer extends PlayerProfile{
	//evaluation for this player profile
	//returns a number bounded from 0 to 1
	public double evaluateLevel(Level level)
	{


		boolean[] enemyInChunk = new boolean[50];

		for (int x = 0; x<200; x++){
			for (int y = level.getHeight()-2; y>0; y--){
				if ( level.getSpriteTemplate(x,y)!=null && (level.getSpriteTemplate(x,y).type == Enemy.ENEMY_RED_KOOPA || level.getSpriteTemplate(x,y).type == Enemy.ENEMY_GREEN_KOOPA || level.getSpriteTemplate(x,y).type == Enemy.ENEMY_GOOMBA) ){
					enemyInChunk[(int)(x/4)] = true;
				}
			}
		}
		

		double score = 0.0;
		double numTrues = 0.0;

		for(int i = 0; i<enemyInChunk.length; i++){
			if(enemyInChunk[i]){
				numTrues+=1.0;
			}
		}

		score = numTrues/50.0;

		if (score>1.0){
			score = 1.0;
		}

		return score;
	}
}