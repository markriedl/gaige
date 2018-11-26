package dk.itu.mario.engine.level;

import java.util.Random;
import java.util.*;


public abstract class DNA implements Comparable<DNA>
{

	protected String chromosome = ""; // The default representation is a string
	private double fitness = 0.0; // Store the fitness
	protected int length = 0; // The length of the level
	
	// Set the chromosome string
	public void setChromosome (String str)
	{
		this.chromosome = str;
		this.length = str.length();
	}
	
	// Get the genotype string
	public String getChromosome ()
	{
		return this.chromosome;
	}
	
	// Set the fitness
	public void setFitness (double fit)
	{
		this.fitness = fit;
	}
	
	// Get the fitness
	public double getFitness ()
	{
		return this.fitness;
	}
	
	// Set the level length
	public void setLength (int n)
	{
		this.length = n;
	}
	
	// Get the level length
	public int getLength ()
	{
		return this.length;
	}
	
	abstract public MyDNA mutate ();
	
	abstract public ArrayList<MyDNA> crossover (MyDNA mate);
	
	public int compareTo (DNA other)
	{
		if (this.fitness == other.getFitness()) {
			return 0;
		}
		else if (this.fitness < other.getFitness()) {
			return -1;
		}
		else {
			return 1;
		}
	}
	
	public String toString ()
	{
		String s = this.getChromosome();
		return s;
	}
}

