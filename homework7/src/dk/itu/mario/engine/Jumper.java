package dk.itu.mario.engine;


import dk.itu.mario.engine.PlayerProfile;
import dk.itu.mario.engine.level.Level;
import dk.itu.mario.engine.sprites.Enemy;

//This player profile wants to be constantly jumping (wants 1 jump per every 4 blocks)
public class Jumper extends PlayerProfile{
	//evaluation for this player profile
	//returns a number bounded from 0 to 1
	public double evaluateLevel(Level level)
	{


		boolean[] jumpInChunk = new boolean[50];

		for (int x = 0; x<200; x++){
			boolean isGap = true;
			for (int y = 13; y<15; y++){
				if(level.getBlock(x,y)!=Level.EMPTY){
					isGap = false;
					break;
				}
			}
			
			if(isGap){
				jumpInChunk[(int)x/4]=true;
			}
			else{
				if ( (level.getBlock(x,12) == Level.TUBE_SIDE_LEFT && level.getBlock(x,13)==Level.HILL_TOP ) || (level.getBlock(x,12) == Level.ROCK && level.getBlock(x,13)==Level.HILL_TOP ) || (level.getBlock(x,12) == Level.CANNON_BASE && level.getBlock(x,13)==Level.HILL_TOP ) || (level.getBlock(x,12) == Level.CANNON_MID && level.getBlock(x,13)==Level.HILL_TOP ) || (level.getBlock(x,12) == Level.CANNON_TOP && level.getBlock(x,13)==Level.HILL_TOP ) ){
					jumpInChunk[(int)(x/4)] = true;
				}
			}
		}
		

		double score = 0.0;
		double numTrues = 0.0;

		for(int i = 0; i<jumpInChunk.length; i++){
			if(jumpInChunk[i]){
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