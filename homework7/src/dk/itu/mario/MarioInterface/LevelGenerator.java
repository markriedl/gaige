package dk.itu.mario.MarioInterface;

import java.io.File;


public interface LevelGenerator {

//Use one of these methods to generate your level
	
	public LevelInterface generateLevel (GamePlay playerMetrics);
	public LevelInterface generateLevel (String detailedInfo);
}
