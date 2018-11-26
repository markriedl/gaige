package dk.itu.mario.engine;


import dk.itu.mario.engine.PlayerProfile;
import dk.itu.mario.engine.level.Level;
import dk.itu.mario.engine.sprites.Enemy;

//This player profile is an even mix of the Scrooge and Killer profiles
public class KillerCollector extends PlayerProfile{
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
		

		double killerScore = 0.0;
		double numTrues = 0.0;

		for(int i = 0; i<enemyInChunk.length; i++){
			if(enemyInChunk[i]){
				numTrues+=1.0;
			}
		}

		killerScore = numTrues/50.0;

		if (killerScore>1.0){
			killerScore = 1.0;
		}

		int numCoins = 0;

		int prevYMin = 12;
		for (int x = 0; x<level.getWidth(); x++){
			int currYMin = 12;
			for (int y = level.getHeight()-2; y>0; y--){
				if (level.getBlock(x,y) == Level.HILL_TOP || level.getBlock(x,y) == Level.CANNON_TOP || level.getBlock(x,y) == Level.TUBE_TOP_LEFT || level.getBlock(x,y) == Level.TUBE_TOP_RIGHT || level.getBlock(x,y) == Level.ROCK){
					currYMin = y;
				}
				if (level.getBlock(x,y) == Level.COIN || (level.getBlock(x,y) == Level.BLOCK_COIN && level.getBlock(x,y+1) == Level.EMPTY) ){
					if(Math.abs(y-currYMin)<5 && Math.abs(y-prevYMin)<5){
						numCoins +=1;
					}
				}
				
			}
			prevYMin = currYMin;
		}
		

		double coinScore = 0.0;
		coinScore = numCoins/100.0;

		if (coinScore>1.0){
			coinScore = 1.0;
		}

		if (numCoins == 0.0 && numTrues == 0.0) {
			return 0;
		}
		double score = ((coinScore + killerScore) / 2.0) * (1 - (Math.abs(numCoins-2*numTrues)/(numCoins+2*numTrues)));

		return score;
	}
}