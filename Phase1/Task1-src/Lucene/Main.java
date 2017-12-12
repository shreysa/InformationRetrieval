
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Scanner;

import org.apache.lucene.document.Document;
import org.apache.lucene.search.ScoreDoc;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;


//Class implementing the main methods
public class Main {

	public static void main(String[] args) throws IOException {
		//Path to the folder where index will be stored
		String indexPath = "E:\\InformationRetrieval\\Assignments\\IR2017_Project\\Index\\LuceneIndex\\";
		Scanner scanner = new Scanner(System.in);

		//Choice to select whether to index or search documents
		System.out.println("**Menu** \n1. Index \n2. Search ");
		int choice = scanner.nextInt();

		switch(choice)
		{
		case 1:
			//Creates an object for the Indexer class.
			Indexer indexer = new Indexer(indexPath);
			try {
				//Path to the folder containing the corpus
				String rawDocs = "E:\\InformationRetrieval\\Assignments\\IR2017_Project\\DataSet\\cacm\\";
				//Index all the files in the corpus
				indexer.indexFiles(rawDocs);
			}
			catch(Exception e) {
				System.out.println("Could not index..." + e.getMessage());
				System.exit(-1);
			}
			break;

		case 2:

			File qFile = new File("E:\\InformationRetrieval\\Assignments\\IR2017_Project\\DataSet\\cacm.query.txt");
			org.jsoup.nodes.Document doc = Jsoup.parse(qFile, "UTF-8", " ");

			doc.select("docno").remove();

			Elements queries = doc.getElementsByTag("doc");
			int qID = 1;
			for (Element query : queries)
			{
				String text = query.text();
				System.out.println(text);
				
				//Creates an object for the searcher class
				Searcher dsearch = new Searcher(indexPath);
				try 
				{
					//Get the results for the given query
					ScoreDoc[] hits = dsearch.getResults(text);
					String filename = "LuceneResults-Query" + Integer.toString(qID) + ".txt";
					String file = "E:\\InformationRetrieval\\Assignments\\IR2017_Project\\SearchResults\\Lucene_Results\\" + filename;
					
					FileWriter fw = new FileWriter(file, true);
					BufferedWriter bw = new BufferedWriter(fw);
					PrintWriter out = new PrintWriter(bw);
					
					//Display the results
					for (int i = 0; i < hits.length; ++i) {
						int docId = hits[i].doc;
						Document d = dsearch.getDoc(docId);
						out.println(qID + " Q0 " + d.get("filename") + " "+ (i+1)
								+ " " + hits[i].score + " LuceneSearch_CF_PUNC");
					}
					System.out.println("Done searching for Query " + qID);
					qID++;
					out.close();
				}
				catch(Exception e) {
					System.out.println("Error Searching " + "" + " : "
							+ e.getMessage());
					qID++;
				}
			}
			break;

		default:
			System.out.println("Invalid choice selected.");	
		}
		scanner.close();
	}
}
