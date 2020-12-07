package com.example.itelliplanterapp;

import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import android.view.View;
import android.widget.EditText;

import com.amazonaws.mobileconnectors.dynamodbv2.document.datatype.Document;

public class CreateNewPlanter extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_create_new_planter);

        Intent intent = getIntent();
    }

    public void newDashboard(View view) {

       Document newPlanter = new Document();
       EditText typeText = (EditText) findViewById(R.id.IntelliPlantType);
       String type = typeText.getText().toString();
       EditText planterIdText = (EditText) findViewById(R.id.IntelliPlanterID);
       String planterId = planterIdText.getText().toString();
       EditText planterNameText = (EditText) findViewById(R.id.IntelliPlanterName);
       String planterName = planterNameText.getText().toString();

       newPlanter.put("PlanterId", planterId);
       newPlanter.put("plantType", type);
       newPlanter.put("planterName", planterName);
       CreateItemAsyncTask task = new CreateItemAsyncTask();
       task.execute(newPlanter);

        Intent intent=new Intent(this, PlanterDashboard.class);

        intent.putExtra("plant", "Plant Type: " + type);
        intent.putExtra("age", "Growing Since: 10/27/2020");
        intent.putExtra("error", "Happy Growing!");
        intent.putExtra("moisture", "Moisture Level: ---");
        intent.putExtra("light", "Light Exposure: ---");
        startActivity(intent);
    }

    /**
     * Async Task to create a new planter into the DynamoDB table
     */
    private class CreateItemAsyncTask extends AsyncTask<Document, Void, Void> {
        @Override
        protected Void doInBackground(Document... documents) {
            DatabaseAccess databaseAccess = DatabaseAccess.getInstance(CreateNewPlanter.this);
            databaseAccess.create(documents[0]);
            return null;
        }
    }
}