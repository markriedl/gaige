package dk.itu.mario.engine;

import dk.itu.mario.engine.level.Level;

public class PlayerProfile{

	
	public PlayerProfile(){}

	//evaluation for this player profile
	//returns a number bounded from 0 to 1
	public double evaluateLevel(Level level)
	{
		return 1.0;
	}

}