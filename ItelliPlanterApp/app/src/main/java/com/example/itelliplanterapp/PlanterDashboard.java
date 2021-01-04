package com.example.itelliplanterapp;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.widget.TextView;

import com.amazonaws.mobileconnectors.dynamodbv2.document.datatype.Document;

import java.text.SimpleDateFormat;
import java.util.Date;

public class PlanterDashboard extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_planter_dashboard);

        Intent intent = getIntent();
        String planterID = intent.getStringExtra("planterID");

        setDashAsyncTask task = new setDashAsyncTask();
        task.execute(planterID);
     }

    private void setDashboard(Document planterInfo) {
        TextView plantType = findViewById(R.id.plantType);
        plantType.setText("Plant Type: " + planterInfo.get("plantType").asString());

        TextView plantAge = findViewById(R.id.plantAge);
        if(planterInfo.get("creationDate") == null){
            plantAge.setText("No date found");
        } else {
            SimpleDateFormat sdf = new SimpleDateFormat("MM/dd/yyyy");
            String date = sdf.format(new Date(planterInfo.get("creationDate").asLong()));
            plantAge.setText("Growing Since: " + date);
        }

        TextView errorFeed = findViewById(R.id.errorFeed);
        if(planterInfo.get("errorMessage") == null) {
            errorFeed.setText("---");
        } else {
            errorFeed.setText(planterInfo.get("errorMessage").asString());
        }

        TextView moistureReading = findViewById(R.id.moistureReading);
        if(planterInfo.get("moisture") == null) {
            moistureReading.setText("Moisture Level: ---");
        } else {
            moistureReading.setText("Moisture Level: " + planterInfo.get("moisture").asString());
        }

        TextView lightReading = findViewById(R.id.lightReading);
        if(planterInfo.get("light") == null){
            lightReading.setText("Light Exposure: ---");
        } else {
            lightReading.setText("Light Exposure: " + planterInfo.get("light").asString());
        }

    }

    private class setDashAsyncTask extends AsyncTask<String, Void, Document> {
        @Override
        protected Document doInBackground(String... planterID) {
            DatabaseAccess databaseAccess = DatabaseAccess.getInstance(PlanterDashboard.this);
            Document planter = databaseAccess.getPlanterById(planterID[0]);
            return planter;
        }
        @Override
        protected void onPostExecute(Document planter) {
            if (planter != null) {
                setDashboard(planter);
            }
        }
    }
}