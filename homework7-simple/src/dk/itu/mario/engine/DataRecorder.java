package dk.itu.mario.engine;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

import dk.itu.mario.MarioInterface.GamePlay;
import dk.itu.mario.engine.sprites.SpriteTemplate;
import dk.itu.mario.engine.sprites.BulletBill;
import dk.itu.mario.engine.sprites.Enemy;
import dk.itu.mario.engine.sprites.Mario;
import dk.itu.mario.engine.sprites.Shell;
import dk.itu.mario.engine.sprites.Sprite;

import dk.itu.mario.engine.level.Level;
import dk.itu.mario.engine.level.MyLevel;
import dk.itu.mario.scene.LevelScene;
import dk.itu.mario.engine.sprites.FlowerEnemy;

public class DataRecorder {

	public boolean recording = true;
	private Level level;
	private boolean []keys, keyPressed;
	private LevelScene levelScene;

	/**
	 * Time variables to record
	 */
	private int timeStart, timeEnd;
	private int completionTime; //counts only the current run on the level, excluding death games
	private int totalTime; //sums all the time, including from previous games if player died

	/**
	 * Jump variables to record
	 */
	private int totalJumpTime, startJumpTime, endJumpTime;
	private int timesJumped;
	public boolean isInAir;

	/**
	 * Duck variables to record
	 */
	private int totalDuckTime, startDuckTime, endDuckTime;
	private int timesDucked;

	/**
	 * Running variables to record
	 */
	private int totalRunTime, startRunTime, endRunTime;
	private int timesRun;

	/**
	 * Switching variables to record
	 */
	private int totalRightTime, totalLeftTime, startRightTime,  endRightTime, startLeftTime, endLeftTime;
	private int direction;

	/**
	 * How many kills the player has
	 */
	private int[] kills;
	private int fireKills;
	private int suicideKills;
	private int stompKills;
	private int shellKills;

	/**
	 * How many times dit the player die to the specific cause (monster or jump)
	 */
	private int[] deaths;

	/**
	 * How many coins did the player collect
	 */
	private int collectedCoins;

	/**
	 * How many blocks did the player destroy
	 */
	private int blocksEmptyDestroyed, blocksCoinDestroyed, blocksPowerDestroyed;

	/**
	 * How many shells the player has kicked
	 */
	private int shellsUnleashed;

	/**
	 * Power up time, how much time mario spent in what form
	 */
	private int totalLittleTime = 0;
	private int startLittleTime = 0;
	private int endLittleTime = 0;

	private int totalLargeTime = 0;
	private int startLargeTime = 0;
	private int endLargeTime = 0;

	private int totalFireTime = 0;
	private int startFireTime = 0;
	private int endFireTime = 0;

	private int switchedPower = 0;

	private boolean levelWon;
	public String detailedLog = "";

	public String getDetailedLog(){
		return detailedLog;
	}
	
	public DataRecorder(LevelScene levelScene, Level level, boolean []keys){
		this.levelScene = levelScene;
		this.level = level;
		this.keys = keys;

		keyPressed = new boolean[keys.length];

		reset();
	}

	public void reset(){
		kills = new int[7];
		deaths = new int[10]; //added one for the hole death and one for time death and one for shell

		//time reset
		completionTime = 0;
		timeStart = 0;
		timeEnd = 0;
		totalTime = 0;

		//jump reset
		timesJumped = 0;
		totalJumpTime = 0;
		startJumpTime = 0;
		endJumpTime = 0;
		isInAir = false;

		//duck reset
		timesDucked = 0;
		totalDuckTime = 0;
		startDuckTime = 0;
		endDuckTime = 0;

		//run reset
		timesRun = 0;
		totalRunTime = 0;
		startRunTime = 0;
		endRunTime = 0;

		//switch reset
		totalRightTime = 0;
		totalLeftTime = 0;
		startRightTime = 0;
		startLeftTime = 0;
		endRightTime = 0;
		endLeftTime = 0;

		//coins reset
		collectedCoins = 0;

		//blocks reset
		blocksEmptyDestroyed = 0;
		blocksCoinDestroyed = 0;
		blocksPowerDestroyed = 0;

		//shell reset
		shellsUnleashed = 0;

		//kill types
		fireKills = 0;
		suicideKills = 0;
		stompKills = 0;
		shellKills = 0;

		//power up types
		totalLittleTime = 0;
		startLittleTime = 0;
		endLittleTime = 0;

		totalLargeTime = 0;
		startLargeTime = 0;
		endLargeTime = 0;

		totalFireTime = 0;
		startFireTime = 0;
		endFireTime = 0;

		switchedPower = 0;

		levelWon = false;
	}

	public void tickRecord(){
		keysRecord();
	}

	public void levelWon(){
		levelWon = true;
	}

	public boolean getLevelWon(){
		return levelWon;
	}

	public void startTime(){
		if(timeStopped == true){
			timeStopped = false;
			timeStart = 2982 - levelScene.timeLeft;
			detailedLog += "StartTime = "+ timeStart;
			detailedLog += "\n";
		}
	}

	private boolean timeStopped = true;
	private long endGRight;

	public void endTime(){
		if(timeStopped == false){
			timeStopped = true;

			timeEnd = 2982 - levelScene.timeLeft;
			totalTime += timeEnd-timeStart;

			completionTime = timeEnd-timeStart;
			detailedLog += "Totaltime = "+completionTime;
			detailedLog += "\n";
		}
	}

	/**
	 * Closes all of the recording, this should commit the data?
	 */
	public void stopRecord(){
		if(recording){
			recording = false;

			//time at current point
			recordJumpLand();
			endTime();

			switch(direction){
				case 1:
					endRightMoveRecord();
				break;
				case -1:
					endLeftMoveRecord();
				break;
			}

			if(levelScene.mario.running){
				endRunningRecord();
			}

			if(levelScene.mario.ducking){
				endDuckRecord();
			}

			if(Mario.large && !Mario.fire){
				endLargeRecord();
			}

			if(Mario.fire){
				endFireRecord();
			}

			if(!Mario.fire && !Mario.large){
				endLittleRecord();
			}
		}
	}

	public void startRightMoveRecord(){
		startRightTime = 2982 - levelScene.timeLeft;
		direction = 1;
	}

	public void startLeftMoveRecord(){
		startLeftTime = 2982 - levelScene.timeLeft;
		direction = -1;
	}

	public void endRightMoveRecord(){
		endRightTime = 2982 - levelScene.timeLeft;

		totalRightTime += endRightTime - startRightTime;
		detailedLog += "RightMove: StTime = "+startRightTime +" EdTime = "+totalRightTime;
		detailedLog += "\n";
	}

	public void endLeftMoveRecord(){
		endLeftTime = 2982 - levelScene.timeLeft;

		totalLeftTime += endLeftTime - startLeftTime;
		detailedLog += "LeftMove: StTime = "+startLeftTime +" EdTime = "+totalLeftTime;
		detailedLog += "\n";

	}

	public void startDuckRecord(){
		if(!levelScene.mario.ducking){
			timesDucked++;

			startDuckTime = 2982 - levelScene.timeLeft;

		}
	}

	public void endDuckRecord(){
		if(levelScene.mario.ducking){
			endDuckTime = 2982 - levelScene.timeLeft;

			totalDuckTime += endDuckTime - startDuckTime;

			
			detailedLog += "Duck: StTime = "+startDuckTime +" EdTime = "+endDuckTime;
			detailedLog += "\n";

		}
	}

	private boolean littleRecording = false;

	public void startLittleRecord(){
		if(!littleRecording){
			littleRecording = true;

			switchedPower++;

			startLittleTime = 2982 - levelScene.timeLeft;
		}
	}

	public void endLittleRecord(){
		if(littleRecording){
			littleRecording = false;
			endLittleTime = 2982 - levelScene.timeLeft;

			totalLittleTime += endLittleTime - startLittleTime;

			detailedLog += "LittleState: StTime = "+startLittleTime +" EdTime = "+endLittleTime;
			detailedLog += "\n";
		}
	}

	public void startLargeRecord(){
		switchedPower++;

		startLargeTime = 2982 - levelScene.timeLeft;

	}

	public void endLargeRecord(){
		endLargeTime = 2982 - levelScene.timeLeft;

		totalLargeTime += endLargeTime - startLargeTime;
		
		detailedLog += "LargeState: StTime = "+startLargeTime +" EdTime = "+endLargeTime;
		detailedLog += "\n";
		
	
	}

	public void startFireRecord(){
		switchedPower++;

		startFireTime = 2982 - levelScene.timeLeft;
	}

	public void endFireRecord(){
		endFireTime = 2982 - levelScene.timeLeft;

		totalFireTime += endFireTime - startFireTime;

		detailedLog += "FireState: StTime = "+startFireTime +" EdTime = "+endFireTime;
		detailedLog += "\n";
	}

	public void startRunningRecord(){
		if(!levelScene.mario.running){
			timesRun++;

			startRunTime = 2982 - levelScene.timeLeft;

		}
	}

	public void endRunningRecord(){
		if(levelScene.mario.running){

			endRunTime = 2982 - levelScene.timeLeft;

			totalRunTime += endRunTime - startRunTime;
			
			detailedLog += "RunState: StTime = "+startRunTime +" EdTime = "+endRunTime;
			detailedLog += "\n";			
			
		}
	}

	public void fireKillRecord(Sprite sprite){
		killRecord(sprite);
		int enemyType = 0;
		if(sprite instanceof FlowerEnemy){
			detailedLog += "FireKill:  EnemyType = FlowerEnemy  time = "+ (2982 - levelScene.timeLeft);
			detailedLog += "\n";		
		}
		else if(sprite instanceof BulletBill){// cannon shot
		}
		else if(sprite instanceof Shell){
		}
		else if(sprite instanceof Enemy){
			Enemy enemy = (Enemy)sprite;
			detailedLog += "FireKill:  EnemyType ="+ enemy.type +"time = "+ (2982 - levelScene.timeLeft);
			detailedLog += "\n";	
		}
		fireKills++;
	}

	public void shellKillRecord(Sprite sprite){
		killRecord(sprite);
		if(sprite instanceof FlowerEnemy){
			detailedLog += "ShellKill:  EnemyType = FlowerEnemy time = "+ (2982 - levelScene.timeLeft);
			detailedLog += "\n";	
		}
		else if(sprite instanceof BulletBill){//cannon shot
		}
		else if(sprite instanceof Shell){
			detailedLog += "ShellKill:  EnemyType = Turtle time = "+ (2982 - levelScene.timeLeft);
			detailedLog += "\n";	
		}
		else if(sprite instanceof Enemy){
			Enemy enemy = (Enemy)sprite;
			detailedLog += "ShellKill:  EnemyType = "+enemy.type+" time = "+ (2982 - levelScene.timeLeft);
			detailedLog += "\n";	
		}
		
		shellKills++;
	}

	public void killSuicideRecord(Sprite sprite){
		killRecord(sprite);
		suicideKills++;
	}

	public void killStompRecord(Sprite sprite){
		killRecord(sprite);
		if(sprite instanceof FlowerEnemy){
			detailedLog += "StompKill:  EnemyType = FlowerEnemy time = "+ (2982 - levelScene.timeLeft);
			detailedLog += "\n";	
			
		}
		else if(sprite instanceof BulletBill){// cannon shot
			detailedLog += "StompKill:  EnemyType = BulletBill time = "+ (2982 - levelScene.timeLeft);
			detailedLog += "\n";				
		}
		else if(sprite instanceof Shell){
//			levelScene.levelRecorder.enemyR.interact.add(new DataEntry(EnemyRecorder.GREEN_TURTLE, EnemyRecorder.UNLEASHED, 2982 - levelScene.timeLeft,x,y));
					}
		else if(sprite instanceof Enemy){
			Enemy enemy = (Enemy)sprite;
			detailedLog += "StompKill:  EnemyType = "+enemy.type+" time = "+ (2982 - levelScene.timeLeft);
			detailedLog += "\n";	
			
		}
		stompKills++;
	}

	public void killRecord(Sprite sprite){
		//something goes wrong with the type of the flower enemy, this is special case
		if(sprite instanceof FlowerEnemy){

			kills[SpriteTemplate.JUMP_FLOWER]++;
		}
		else if(sprite instanceof BulletBill){
			kills[5]++;
		}
		else if(sprite instanceof Shell){
			//not sure what to do with shells
		}
		else if(sprite instanceof Enemy){
			Enemy enemy = (Enemy)sprite;

			kills[enemy.type]++;
		}

		//printKills();
	}

	public void blockEmptyDestroyRecord(){
		
		blocksEmptyDestroyed++;
	}

	public void blockCoinDestroyRecord(){
		detailedLog += "BlockCoinDestroy:  time = "+ (2982 - levelScene.timeLeft);
		detailedLog += "\n";	
		blocksCoinDestroyed++;
	}

	public void blockPowerDestroyRecord(){
		detailedLog += "BlockPowerDestroy:  time = "+ (2982 - levelScene.timeLeft);
		detailedLog += "\n";	
		blocksPowerDestroyed++;
	}

	public void dieRecord(Sprite sprite){
		if(sprite instanceof FlowerEnemy){
			detailedLog += "Die:  EnemyType = FlowerEnemy ";
			detailedLog += "\n";	
			deaths[SpriteTemplate.JUMP_FLOWER]++;
		}
		else if(sprite instanceof BulletBill){
			detailedLog += "Die:  EnemyType = BulletBill ";
			detailedLog += "\n";
			deaths[5]++;
		}
		else if(sprite instanceof Shell){
			//not sure what to do with shells
			detailedLog += "Die:  EnemyType = TurtleShell ";
			detailedLog += "\n";
			deaths[9]++;
		}
		else if(sprite instanceof Enemy){
			Enemy enemy = (Enemy)sprite;
			deaths[enemy.type]++;
			detailedLog += "Die:  EnemyType = "+enemy.type;
			detailedLog += "\n";
			
		}


	}

	public void dieTimeRecord(){
		//time
		deaths[7]++;

	}

	public void dieJumpRecord(){
		//jump
		deaths[8]++;
		detailedLog += "Die:  Gap ";
		detailedLog += "\n";

	}

	public void shellUnleashedRecord(){
		shellsUnleashed++;
		detailedLog += "UnleashShell:  time = "+ (2982 - levelScene.timeLeft);
		detailedLog += "\n";
	}

	private void keysRecord(){
		if(keys[Mario.KEY_LEFT] && !keyPressed[Mario.KEY_LEFT]){
			keyPressed[Mario.KEY_LEFT] = true;
		}
		else if(!keys[Mario.KEY_LEFT]){
			keyPressed[Mario.KEY_LEFT] = false;
		}
	}

	public void recordJump(){
		if(isInAir){
			timesJumped++;
			startJumpTime = 2982 -levelScene.timeLeft;
		}
	}

	public void recordJumpLand(){
		if(isInAir){
			isInAir = false;
			endJumpTime = 2982-levelScene.timeLeft;

			totalJumpTime += endJumpTime - startJumpTime;
				
			detailedLog += "Jump:  StTime = "+ startJumpTime +" EdTime = "+endJumpTime;
			detailedLog += "\n";
		}
	}

	public void recordCoin(){
		detailedLog += "CollectCoin:  time = "+ (2982 - levelScene.timeLeft);
		detailedLog += "\n";
		collectedCoins++;
	}

	private int convertTime(int time){
		return (int)Math.floor((time+15-1)/15);
	}

	public void printAll(){

		printKills();
		printTime();
		printJump();
		printDuck();
		printRun();
		printSwitching();

	}

	private void printSwitching(){
		printStart("Switch Variables");

		printEnd();
	}

	private void printJump(){
		printStart("Jump Variables");
		printEnd();
	}

	private void printRun(){
		printStart("Run Variables");
		printEnd();
	}

	private void printDuck(){
		printStart("Duck Variables");
		printEnd();
	}

	private void printTime(){
		printStart("Time Variables");
		printEnd();
	}

	private void printDeaths(){
		printStart("Player Died Against");
		int deathsTotal = 0;

		for(int i=0;i<deaths.length;++i){
			String type = "";

			switch(i){
				case SpriteTemplate.RED_TURTLE:
					type = "Red Koopa";
				break;
				case SpriteTemplate.GREEN_TURTLE:
					type = "Green Koopa";
				break;
				case SpriteTemplate.GOOMPA:
					type = "Goompa";
				break;
				case SpriteTemplate.ARMORED_TURTLE:
					type = "Spikey Turtle";
				break;
				case SpriteTemplate.JUMP_FLOWER:
					type = "Jumping Flower";
				break;
				case SpriteTemplate.CANNON_BALL:
					type = "Cannon Ball";
				break;
				case SpriteTemplate.CHOMP_FLOWER:
					type = "Chomping Flower";
				break;
				case 7:
					type = "Time";
				break;
				case 8:
					type = "Hole";
				break;
				case 9:
					type = "Shell";
				break;
			}


			deathsTotal+= deaths[i];
		}


		printEnd();

	}

	private void printKills(){
		printStart("Player Has Killed");

		for(int i=0;i<kills.length;++i){
			String type = "";

			switch(i){
				case SpriteTemplate.RED_TURTLE:
					type = "Red Koopa";

				break;
				case SpriteTemplate.GREEN_TURTLE:
					type = "Green Koopa";
				break;
				case SpriteTemplate.GOOMPA:
					type = "Goompa";
				break;
				case SpriteTemplate.ARMORED_TURTLE:
					type = "Spikey Turtle";
				break;
				case SpriteTemplate.JUMP_FLOWER:
					type = "Jumping Flower";
				break;
				case SpriteTemplate.CANNON_BALL:
					type = "Cannon Ball";
				break;
				case SpriteTemplate.CHOMP_FLOWER:
					type = "Chomping Flower";
				break;
			}

			int percentage = 0;

		}

		printEnd();
	}

	private void printStart(String title){
		title = " "+title+" ";

		int tweak = 0;
		if(title.length()%2!=0) //unequal number
			tweak = 1;


		for(int i=0;i<50/2-title.length()/2;++i)
			System.out.print(">");

		System.out.print(title);

		for(int i=0;i<50/2-title.length()/2 - tweak;++i)
			System.out.print("<");

		System.out.print("\n");

	}

	private void printEnd(){

		for(int i=0;i<50;++i)
			System.out.print("-");

		System.out.print("\n");
	}

	public void fillGamePlayMetrics(MyLevel level){
        GamePlay gpm = new GamePlay();
		gpm.completionTime = getCompletionTime();
		gpm.totalTime = getTotalTime();////sums all the time, including from previous games if player died
		gpm.jumpsNumber = getTimesJumped();
		gpm.timeSpentDucking = getTotalDuckTime();
		gpm.duckNumber = getTimesDucked();
		gpm.timeSpentRunning = getTotalRunTime();
		gpm.timesPressedRun = getTimesRun();
		gpm.timeRunningRight = getTotalRightTime();
		gpm.timeRunningLeft =  getTotalLeftTime();
		gpm.coinsCollected =  getCoinsCollected();
		gpm.totalCoins = level.COINS;
		gpm.emptyBlocksDestroyed = getBlocksEmptyDestroyed();
		gpm.totalEmptyBlocks = level.BLOCKS_EMPTY;
		gpm.coinBlocksDestroyed = getBlocksCoinDestroyed();
		gpm.totalCoinBlocks = level.BLOCKS_COINS;
		gpm.powerBlocksDestroyed = getBlocksPowerDestroyed();
		gpm.totalpowerBlocks = level.BLOCKS_POWER;
		gpm.kickedShells =  getShellsUnleashed(); //kicked
		gpm.enemyKillByFire = getKillsFire();//Number of Kills by Shooting Enemy
		gpm.enemyKillByKickingShell = getKillsShell();//Number of Kills by Kicking Shell on Enemy
		gpm.totalEnemies = level.ENEMIES;

		gpm.totalTimeLittleMode = getTotalLittleTime();
		gpm.totalTimeLargeMode = getTotalLargeTime();//Time Spent Being Large Mario
		gpm.totalTimeFireMode = getTotalFireTime();//Time Spent Being Fire Mario
		gpm.timesSwichingPower = getSwitchedPower();//Number of Times Switched Between Little, Large or Fire Mario
		gpm.aimlessJumps = J();//aimless jumps
		//gpm.percentageBlocksDestroyed = nb();//percentage of all blocks destroyed
		//gpm.percentageCoinBlocksDestroyed = ncb();//percentage of coin blocks destroyed
		//gpm.percentageEmptyBlockesDestroyed = neb();//percentage of empty blocks destroyed
		//gpm.percentagePowerBlockDestroyed = np();//percentage of power blocks destroyed
		//gpm.timesOfDeathByFallingIntoGap = dg();//number of death by falling into a gap
		gpm.timesOfDeathByRedTurtle = deaths[SpriteTemplate.RED_TURTLE];
		gpm.timesOfDeathByGreenTurtle = deaths[SpriteTemplate.GREEN_TURTLE];
		gpm.timesOfDeathByGoomba = deaths[SpriteTemplate.GOOMPA];
		gpm.timesOfDeathByArmoredTurtle = deaths[SpriteTemplate.ARMORED_TURTLE];
		gpm.timesOfDeathByJumpFlower = deaths[SpriteTemplate.JUMP_FLOWER];
		gpm.timesOfDeathByCannonBall = deaths[SpriteTemplate.CANNON_BALL];
		gpm.timesOfDeathByChompFlower = deaths[SpriteTemplate.CHOMP_FLOWER];

		gpm.RedTurtlesKilled = kills[SpriteTemplate.RED_TURTLE];
		gpm.GreenTurtlesKilled = kills[SpriteTemplate.GREEN_TURTLE];
		gpm.GoombasKilled = kills[SpriteTemplate.GOOMPA];
		gpm.ArmoredTurtlesKilled = kills[SpriteTemplate.ARMORED_TURTLE];
		gpm.JumpFlowersKilled = kills[SpriteTemplate.JUMP_FLOWER];
		gpm.CannonBallKilled = kills[SpriteTemplate.CANNON_BALL];
		gpm.ChompFlowersKilled = kills[SpriteTemplate.CHOMP_FLOWER];
		gpm.write("player.txt");
		//System.out.println(detailedLog);
		write(detailedLog);
		
	}

	public void WriteDetailedLog(){
		write(detailedLog);
	}



	private void write(String detailedLog2) {
		try {
			String filePath = "DetailedInfo.txt";//getClass().getProtectionDomain().getCodeSource().getLocation()+"DetailedInfo.txt";
			File yourFile = new File(filePath);
			
			if(!yourFile.exists()){
				try{
					yourFile.createNewFile();
				}
				catch (IOException e) {
					
					e.printStackTrace();
				}
			}
			FileWriter file = new FileWriter(yourFile);
			file.write(detailedLog);
			file.close();
		} catch (IOException e) {
			
			e.printStackTrace();
		}
		
	}

	public int getCompletionTime(){
		return convertTime(completionTime);
	}

	public int getTotalTime(){
		return convertTime(totalTime);
	}

	public int getTotalJumpTime(){
		return convertTime(totalJumpTime);
	}

	public int getTimesJumped(){
		return timesJumped;
	}

	public int getTotalDuckTime(){
		return convertTime(totalDuckTime);
	}

	public int getTimesDucked(){
		return timesDucked;
	}

	public int getTotalRunTime(){
		return convertTime(totalRunTime);
	}

	public int getTimesRun(){
		return timesRun;
	}

	public int getTotalRightTime(){
		return convertTime(totalRightTime);
	}

	public int getTotalLeftTime(){
		return convertTime(totalLeftTime);
	}

	public int getCoinsCollected(){
		return collectedCoins;
	}

	public int getBlocksEmptyDestroyed(){
		return blocksEmptyDestroyed;
	}

	public int getBlocksCoinDestroyed(){
		return blocksCoinDestroyed;
	}

	public int getBlocksPowerDestroyed(){
		return blocksPowerDestroyed;
	}

	public int getKills(int monster){
		return kills[monster];
	}

	public int getDeaths(int cause){
		return deaths[cause];
	}

	public int getShellsUnleashed(){
		return shellsUnleashed;
	}

	public int getKillsStomp(){
		return stompKills;
	}

	public int getKillsFire(){
		return fireKills;
	}

	public int getKillsShell(){
		return shellKills;
	}

	public  int getKillsSuicide(){
		return suicideKills;
	}

	public int getTotalLittleTime(){
		return convertTime(totalLittleTime);
	}

	public int getTotalLargeTime(){
		return convertTime(totalLargeTime);
	}

	public int getTotalFireTime(){
		return convertTime(totalFireTime);
	}

	public int getSwitchedPower(){
		return switchedPower;
	}


	/**
	 * The total time taken to complete a level
	 * @return
	 */
	public double tc(){
		return (double)getTotalTime();
	}

	public double tL(){
		return (double)getTotalLeftTime()/(double)getTotalTime();
	}

	/**
	 * time in large form
	 * @return
	 */
	public double tl(){
		return (double)getTotalLargeTime()/(double)getTotalTime();
	}

	/**
	 * Time in tiny mario form
	 * @return
	 */
	public double tt(){
		return (double)getTotalLittleTime()/(double)getTotalTime();
	}

	/**
	 * Time spent running in percent
	 * @return
	 */
	public double tr(){
		return (double)getTotalRunTime()/(double)getTotalTime();
	}

	/**
	 * Time spent in powerup form
	 * @return
	 */
	public double tp(){
		return 1-((double)getTotalLittleTime()/(double)getTotalTime());
	}

	/**
	 * Time spent in fire mario form
	 * @return
	 */
	public double tf(){
		return (double)getTotalFireTime()/(double)getTotalTime();
	}

	public double tR(){
		return (double)getTotalRightTime()/(double)getTotalTime();
	}

	public double ks(){
		if(getKillsStomp()+getKillsFire() == 0){
			return 0;
		}
		else
			return (double)getKillsStomp()/(double)(getKillsStomp()+getKillsFire());
	}

	public double kf(){
		if(getKillsFire()+getKillsStomp() == 0)
			return 0;
		else
			return (double)getKillsFire()/(double)(getKillsFire()+getKillsStomp());
	}

	public double tll(){
		return getCompletionTime();
	}

	public double ts(){
		return 1-((getTotalLeftTime()+getTotalRightTime())/getTotalTime());
	}

	/**
	 * This is also called J' but cant be called that due to special character
	 * @return double of aimless jumps
	 */
	public double J(){
		return getTimesJumped()-getKillsStomp()-getBlocksEmptyDestroyed()-getBlocksCoinDestroyed()-getBlocksPowerDestroyed();
	}

	public double nm(){
		return getSwitchedPower();
	}

	public double nd(){
		return getTimesDucked();
	}

	/**
	 * Percentage of all blocks destroyed
	 * @return
	 */
	/**
	public double nb(){
		double n = 0;
		if( level.BLOCKS_EMPTY != 0)
			n+= getBlocksEmptyDestroyed()/level.BLOCKS_EMPTY;
		if(level.BLOCKS_POWER != 0)
			n+= getBlocksPowerDestroyed()/level.BLOCKS_POWER;
		if( level.BLOCKS_COINS != 0)
			n+= getBlocksCoinDestroyed()/level.BLOCKS_COINS;

		return n;
	}

	public double ncb(){
		if( level.BLOCKS_COINS != 0)
			return getBlocksCoinDestroyed()/level.BLOCKS_COINS;
		else
			return 0;
	}

	public double neb(){
		if( level.BLOCKS_EMPTY != 0)
			return getBlocksEmptyDestroyed()/level.BLOCKS_EMPTY;
		else
			return 0;
	}

	public double np(){
		if( level.BLOCKS_POWER != 0)
			return getBlocksPowerDestroyed()/level.BLOCKS_POWER;
		else
			return 0;
	}
	*/

	/**
	 * Deaths by falling into gaps
	 * @return
	 */
	//public double dg(){
	//	return getDeaths(8);
	//}

	/**
	 * Percentage of deaths by falling into gaps
	 * @return
	 */
	/**
	public double dj(){
		int tDeaths = 0;

		for(int i=0;i<deaths.length;++i){
			tDeaths += deaths[i];
		}

		if(tDeaths<=0)
			return 0;
		else
			return dg()/tDeaths;
	}
	*/
	/**
	 * should be do but cannot use constrained word
	 * @return
	 */
	/**
	public double dop(){
		int deaths = 0;

		for(int i=0;i<=6;++i)
			deaths += getDeaths(i);

		return deaths+getDeaths(9); //remember the shell
	}
	*/

	public static double normalize(double v, double min, double max){
		double out = (v-min)/(max-min);

		if(out > 1)
			return 1;
		else if(out < 0)
			return 0;
		else
			return out;
	}
}
