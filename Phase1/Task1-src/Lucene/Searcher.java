
import java.io.File;
import java.io.IOException;

import org.apache.lucene.analysis.core.SimpleAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopScoreDocCollector;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;

// class to implement the search part of lucene
public class Searcher {

	IndexSearcher isearcher;
	QueryParser queryParser;
	Query query;
	//Number of hits required
	int MAX_SEARCH = 100;
	
	//Constructor
	public Searcher(String indexLoc) throws IOException
	{
		Directory indexDir = FSDirectory.open(new File(indexLoc));
		isearcher = new IndexSearcher(DirectoryReader.open(indexDir));
		queryParser = new QueryParser(Version.LUCENE_47, "contents", 
				new SimpleAnalyzer(Version.LUCENE_47));
	}
	
	//Function returns the list of documents in an array.
	public ScoreDoc[] getResults(String q) throws IOException, ParseException
	{
		query = queryParser.parse(q);
		TopScoreDocCollector collector = TopScoreDocCollector.create(this.MAX_SEARCH, true);
		
		isearcher.search(query, collector);
		return collector.topDocs().scoreDocs;
	}
	
	//Function returns the Document for the given document ID
	public Document getDoc(int docID) throws IOException
	{
		return isearcher.doc(docID);
	}
}
