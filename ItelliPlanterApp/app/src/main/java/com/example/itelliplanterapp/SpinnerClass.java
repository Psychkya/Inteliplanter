package com.example.itelliplanterapp;

import java.util.ArrayList;
import java.util.List;
import android.app.Activity;
import android.os.AsyncTask;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Spinner;
import android.widget.Toast;
import android.widget.AdapterView.OnItemSelectedListener;

import com.amazonaws.mobileconnectors.dynamodbv2.document.datatype.Document;
import com.example.itelliplanterapp.DatabaseAccess;
import com.example.itelliplanterapp.MainActivity;
import com.example.itelliplanterapp.R;

class SpinnerClass extends Activity implements OnItemSelectedListener{
    public List<String> planterOptions = new ArrayList<>();
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        GetAllItemsAsyncTask task = new GetAllItemsAsyncTask();
        task.execute();

        Spinner spinner = (Spinner) findViewById(R.id.planterSpinner);
        // Spinner click listener
        spinner.setOnItemSelectedListener(this);
        // Create an ArrayAdapter using the string array and a default spinner layout
        ArrayAdapter<String> adapter = new ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_item, planterOptions);
        // Specify the layout to use when the list of choices appears
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        // Apply the adapter to the spinner
        spinner.setAdapter(adapter);
    }

    public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
        // On selecting a spinner item
        String item = parent.getItemAtPosition(position).toString();

        // Showing selected spinner item
        Toast.makeText(parent.getContext(), "Selected: " + item, Toast.LENGTH_LONG).show();
    }
    public void onNothingSelected(AdapterView<?> arg0) {
        // TODO Auto-generated method stub
    }

    private class GetAllItemsAsyncTask extends AsyncTask<Void, Void,List<String>> {
        @Override
        protected List<String> doInBackground(Void... params) {
            DatabaseAccess databaseAccess = DatabaseAccess.getInstance(SpinnerClass.this);
            List<Document> results = databaseAccess.getAllPlanters();
            for (Document planter:results) {
                planterOptions.add(planter.get("planterName").asString());
            }
            return planterOptions;
        }
    }

}
