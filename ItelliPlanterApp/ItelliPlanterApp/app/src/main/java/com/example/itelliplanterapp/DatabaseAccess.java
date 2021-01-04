package com.example.itelliplanterapp;

import android.content.Context;

import com.amazonaws.auth.CognitoCachingCredentialsProvider;
import com.amazonaws.mobileconnectors.dynamodbv2.document.ScanOperationConfig;
import com.amazonaws.mobileconnectors.dynamodbv2.document.Search;
import com.amazonaws.mobileconnectors.dynamodbv2.document.Table;
import com.amazonaws.mobileconnectors.dynamodbv2.document.datatype.Document;
import com.amazonaws.mobileconnectors.dynamodbv2.document.datatype.Primitive;
import com.amazonaws.regions.Region;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClient;
import com.amazonaws.services.dynamodbv2.model.AttributeValue;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class DatabaseAccess {

    private final String COGNITO_IDENTITY_POOL_ID = "us-west-2:0229c674-628f-4def-8cd1-ecddc28aade7";
    private final Regions COGNITO_IDENTITY_POOL_REGION = Regions.US_WEST_2;
    private final String DYNAMODB_TABLE = "IntelliPlanter";
    private Context context;
    private CognitoCachingCredentialsProvider credentialsProvider;
    private AmazonDynamoDBClient dbClient;
    private Table dbTable;

    private static volatile DatabaseAccess instance;

    private DatabaseAccess(Context context) {
        this.context = context;

        //Create a new credentials provider
        credentialsProvider = new CognitoCachingCredentialsProvider(context, COGNITO_IDENTITY_POOL_ID, COGNITO_IDENTITY_POOL_REGION);
        // Create a connection to the DynamoDB service
        dbClient = new AmazonDynamoDBClient(credentialsProvider);
        /*MUST SET db client REGION ELSE DEFAULTS TO US_EAST_1*/
        dbClient.setRegion(Region.getRegion(Regions.US_WEST_2));
        // Create a table reference
        dbTable = Table.loadTable(dbClient, DYNAMODB_TABLE);
    }

    /**
     * Singleton pattern - retrieve an instance of the DatabaseAccess
     */

    public static synchronized DatabaseAccess getInstance(Context context) {
        if (instance == null) {
            instance = new DatabaseAccess(context);
        }
        return instance;
    }

    public void create(Document planter) {
        if (!planter.containsKey("creationDate")) {
            planter.put("creationDate", System.currentTimeMillis());
        }
        dbTable.putItem(planter);
    }

    public Document getPlanterById(String planterId) {
        Document result = dbTable.getItem(new Primitive(planterId));
        return result;
    }

    public List<Document> getAllPlanters() {
        ScanOperationConfig scanConfig = new ScanOperationConfig();
        List<String> attrList = new ArrayList<>();
        attrList.add("planterName");
        attrList.add("PlanterId");
        scanConfig.withAttributesToGet(attrList);
        Search results = dbTable.scan(scanConfig);
        return results.getAllResults();
    }
}
