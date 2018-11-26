package dk.itu.mario.MarioInterface;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;

public class GamePlay implements Serializable {
		
	private static final long serialVersionUID = 1L;
	
	public int completionTime; //counts only the current run on the level, excluding death games
	public int totalTime;//sums all the time, including from previous games if player died
	public int jumpsNumber; // total number of jumps
	public int duckNumber; //total number of ducks
	public int timeSpentDucking; // time spent in ducking mode
	public int timesPressedRun;//number of times the run key pressed
	public int timeSpentRunning; //total time spent running
	public int timeRunningRight; //total time spent running to the right
	public int timeRunningLeft;//total time spent running to the left
	public int emptyBlocksDestroyed; //number of empty blocks destroyed
	public int coinsCollected; //number of coins collected
	public int coinBlocksDestroyed; //number of coin block destroyed
	public int powerBlocksDestroyed; //number of power block destroyed
	public int kickedShells; //number of shells Mario kicked
	public int enemyKillByFire; //number of enemies killed by shooting them
	public int enemyKillByKickingShell; //number of enemies killed by kicking a shell on them
	public int totalTimeLittleMode; //total time spent in little mode
	public int totalTimeLargeMode; //total time spent in large mode
	public int totalTimeFireMode; //total time spent in fire mode
	public int timesSwichingPower; //number of Times Switched Between Little, Large or Fire Mario
	public double aimlessJumps; //number of jumps without a reason
	public double percentageBlocksDestroyed; //percentage of all blocks destroyed
	public double percentageCoinBlocksDestroyed; //percentage of coin blocks destroyed
	public double percentageEmptyBlockesDestroyed; //percentage of empty blocks destroyed
	public double percentagePowerBlockDestroyed; //percentage of power blocks destroyed
	public double timesOfDeathByFallingIntoGap; //number of death by falling into a gap
	public int totalEnemies; //total number of enemies
	public int totalEmptyBlocks; //total number of empty blocks
	public int totalCoinBlocks; //total number of coin blocks
	public int totalpowerBlocks; //total number of power blocks
	public int totalCoins; //total number of coins
	public int timesOfDeathByRedTurtle; //number of times Mario died by red turtle
	public int timesOfDeathByGoomba; //number of times Mario died by Goomba
	public int timesOfDeathByGreenTurtle; //number of times Mario died by green turtle
	public int timesOfDeathByArmoredTurtle; //number of times Mario died by Armored turtle
	public int timesOfDeathByJumpFlower; //number of times Mario died by Jump Flower
	public int timesOfDeathByCannonBall; //number of time Mario died by Cannon Ball
	public int timesOfDeathByChompFlower; //number of times Mario died by Chomp Flower
	public int RedTurtlesKilled; //number of Red Turtle Mario killed
	public int GreenTurtlesKilled;//number of Green Turtle Mario killed
	public int ArmoredTurtlesKilled; //number of Armored Turtle Mario killed
	public int GoombasKilled; //number of Goombas Mario killed
	public int CannonBallKilled; //number of Cannon Ball Mario killed
	public int JumpFlowersKilled; //number of Jump Flower Mario killed
	public int ChompFlowersKilled; //number of Chomp Flower Mario killed
	
	public void write(String fileName){
		ObjectOutputStream out = null;
		try {
			FileOutputStream fos = new FileOutputStream(fileName);
			out =  new ObjectOutputStream(fos);
			out.writeObject(this);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}
	
	public static GamePlay read(String fileName){
		FileInputStream fis = null;
	    ObjectInputStream in = null;
	    GamePlay gp =  null;
		try {
			fis = new FileInputStream(fileName);
			in = new ObjectInputStream(fis);
			gp = (GamePlay)in.readObject();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return gp;
	}
}
