package dk.itu.mario.engine.level;

import java.util.Random;
import java.util.*;

//Make any new member variables and functions you deem necessary.
//Make new constructors if necessary
//You must implement mutate() and crossover()


public class MyDNA extends DNA
{

	public int numGenes = 0; //number of genes

	// Use these constants to make your DNA strings.

	// Represents a gap in the floor that Mario can fall through and die.
	public static final char GAP_CHAR = 'G';
	// Represents a straight, flat section of ground.
	public static final char STRAIGHT_CHAR = 'S';
	// Represents ground with coins above it.
	public static final char COINS_CHAR = 'C';
	// Represents a set of stairs that Mario needs to jump over.
	public static final char HILL_CHAR = 'H';
	// Represents ground with monsters over it (e.g., goombas, koopas).
	public static final char MONSTERS_CHAR = 'M';

	// Return a new DNA that differs from this one in a small way.
	// Do not change this DNA by side effect; copy it, change the copy, and return the copy.
	public MyDNA mutate ()
	{
		MyDNA copy = new MyDNA();
		//YOUR CODE GOES BELOW HERE

		//YOUR CODE GOES ABOVE HERE
		return copy;
	}

	// Do not change this DNA by side effect
	public ArrayList<MyDNA> crossover (MyDNA mate)
	{
		ArrayList<MyDNA> offspring = new ArrayList<MyDNA>();
		//YOUR CODE GOES BELOW HERE

		//YOUR CODE GOES ABOVE HERE
		return offspring;
	}

	// Optional, modify this function if you use a means of calculating fitness other than using the fitness member variable.
	// Return 0 if this object has the same fitness as other.
	// Return -1 if this object has lower fitness than other.
	// Return +1 if this objet has greater fitness than other.
	public int compareTo(MyDNA other)
	{
		int result = super.compareTo(other);
		//YOUR CODE GOES BELOW HERE

		//YOUR CODE GOES ABOVE HERE
		return result;
	}


	// For debugging purposes (optional)
	public String toString ()
	{
		String s = super.toString();
		//YOUR CODE GOES BELOW HERE

		//YOUR CODE GOES ABOVE HERE
		return s;
	}

	public void setNumGenes (int n)
	{
		this.numGenes = n;
	}

}

