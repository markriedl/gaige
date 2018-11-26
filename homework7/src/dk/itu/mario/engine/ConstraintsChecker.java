package dk.itu.mario.engine;

import dk.itu.mario.engine.level.Level;
import dk.itu.mario.MarioInterface.Constraints;
import dk.itu.mario.engine.sprites.SpriteTemplate;

public final class ConstraintsChecker {

	public static boolean check(Level level){
		if(level.getWidth() != Constraints.levelWidth)
			return false;
		//check the number of gaps
		int levelGaps = 0, bcoins = 0;
		for (int i = 0; i < level.getWidth(); i++) {
			if (level.getBlock(i, level.getHeight()) == 0){
				levelGaps++;
				while (i<level.getWidth() && level.getBlock(i, level.getHeight())==0){
					i++;
				}
			}

		}
//		if(levelGaps != Constraints.gaps)
//			return false;

		//check the number of TURTLES
		int tur = 0;
		for (int i = 0; i < level.getSpriteTemplate().length; i++) {

				SpriteTemplate[] st = (SpriteTemplate[])level.getSpriteTemplate()[i];
				for (int j = 0; j < st.length; j++) {
					if(st[j]!=null){
						int t = ((SpriteTemplate)st[j]).type;
						if(t== SpriteTemplate.RED_TURTLE || t == SpriteTemplate.GREEN_TURTLE || t == SpriteTemplate.ARMORED_TURTLE)
							tur++;
					}
			}
		}
//		if(tur != Constraints.turtels)
//			return false;

		//check the number of coin blocks
		for (int i = 0; i < level.getWidth(); i++) {
			for (int j = 0; j < level.getHeight(); j++) {
				 byte block = level.getBlock(i, j);
				 if ((Level.TILE_BEHAVIORS[block & 0xff] & Level.BIT_BUMPABLE) > 0)
					 if (! (((Level.TILE_BEHAVIORS[block & 0xff]) & Level.BIT_SPECIAL) > 0))
						 bcoins++;
			}
		}
//		if(bcoins != Constraints.coinBlocks)
//			return false;
		return true;
	}

}
