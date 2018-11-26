package dk.itu.mario.engine;


import dk.itu.mario.engine.PlayerProfile;
import dk.itu.mario.engine.level.Level;

//This Player Profile simply wants to see a lot of coins or blocks with coins (1 every 2 blocks)
public class Scrooge extends PlayerProfile{
	//evaluation for this player profile
	//returns a number bounded from 0 to 1
	public double evaluateLevel(Level level)
	{
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
		

		double score = 0.0;
		score = numCoins/100.0;

		if (score>1.0){
			score = 1.0;
		}
		
		return score;
	}
}