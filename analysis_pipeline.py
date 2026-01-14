import os
import time
import json
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from sqlalchemy.orm import Session
from database.database import engine
from models import Result, Initiative, Grant, Organisation

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Model configuration - using gemini-3-flash-preview for all calls
MODEL_NAME = "gemini-3-flash-preview"

# Rate limiting configuration (15 requests per minute for free tier)
RATE_LIMIT_DELAY = 4.5  # seconds between requests (60/15 = 4, adding buffer)


def rate_limit_sleep():
    """Sleep to respect API rate limits."""
    time.sleep(RATE_LIMIT_DELAY)


def scan_folder_for_pdfs(base_dir: str) -> Dict[int, List[str]]:
    """
    Scans a directory for grant PDFs organized in grant_{id} subfolders.
    
    Args:
        base_dir: Base directory containing grant_{id} folders
        
    Returns:
        Dictionary mapping grant_id to list of PDF file paths
    """
    pdf_map = {}
    
    if not os.path.exists(base_dir):
        print(f"Warning: Directory {base_dir} does not exist")
        return pdf_map
    
    # Find all grant_{id} folders
    grant_folders = glob.glob(os.path.join(base_dir, "grant_*"))
    
    for folder in grant_folders:
        # Extract grant_id from folder name
        folder_name = os.path.basename(folder)
        try:
            grant_id = int(folder_name.split("_")[1])
        except (IndexError, ValueError):
            print(f"Warning: Invalid folder name format: {folder_name}")
            continue
        
        # Find all PDFs in this folder
        pdf_files = glob.glob(os.path.join(folder, "*.pdf"))
        
        if pdf_files:
            pdf_map[grant_id] = pdf_files
            print(f"Found {len(pdf_files)} PDF(s) for grant_id {grant_id}")
    
    return pdf_map


def upload_pdfs_to_gemini(pdf_paths: List[str]) -> List:
    """
    Uploads multiple PDFs to Gemini and returns file references.
    
    Args:
        pdf_paths: List of PDF file paths
        
    Returns:
        List of uploaded file objects
    """
    uploaded_files = []
    
    for pdf_path in pdf_paths:
        try:
            print(f"Uploading {os.path.basename(pdf_path)}...")
            uploaded_file = genai.upload_file(pdf_path)
            uploaded_files.append(uploaded_file)
            rate_limit_sleep()  # Rate limit after upload
        except Exception as e:
            print(f"Error uploading {pdf_path}: {e}")
    
    return uploaded_files


def run_prelim_scan(initiative_id: int, initial_pdf_dir: str):
    """
    Step 1: Preliminary scan of initial grant PDFs.
    Rates relevance 0-100 and saves to Result.prelim_rating.
    
    This function DIRECTLY UPDATES THE DATABASE using SQLAlchemy ORM:
    - Creates a Session object which manages database transactions
    - Queries for existing Result rows using session.query()
    - Either updates existing rows or creates new Result objects
    - Calls session.commit() to persist changes to PostgreSQL
    - Uses session.rollback() on errors to undo changes
    
    Args:
        initiative_id: ID of the initiative to analyze against
        initial_pdf_dir: Directory containing initial grant PDFs
    """
    print(f"\n{'='*60}")
    print(f"STEP 1: Running Preliminary Scan for Initiative {initiative_id}")
    print(f"{'='*60}\n")
    
    session = Session(engine)
    
    try:
        # Get initiative details
        initiative = session.query(Initiative).filter_by(id=initiative_id).first()
        if not initiative:
            print(f"Error: Initiative {initiative_id} not found")
            return
        
        # Get organisation details (there's only one organisation)
        organisation = session.query(Organisation).filter_by(id=initiative.organisation_id).first()
        if not organisation:
            print(f"Error: Organisation {initiative.organisation_id} not found")
            return
        
        print(f"Organisation: {organisation.name}")
        print(f"Mission: {organisation.mission_and_focus[:100]}...")
        print(f"\nInitiative: {initiative.title}")
        print(f"Goals: {initiative.goals[:100]}...")
        print(f"Audience: {initiative.audience}\n")
        
        # Scan for PDFs
        pdf_map = scan_folder_for_pdfs(initial_pdf_dir)
        
        if not pdf_map:
            print(f"No PDFs found in {initial_pdf_dir}")
            return
        
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Process each grant
        for grant_id, pdf_paths in pdf_map.items():
            print(f"\n--- Processing Grant ID: {grant_id} ---")
            
            # Verify grant exists
            grant = session.query(Grant).filter_by(id=grant_id).first()
            if not grant:
                print(f"Warning: Grant {grant_id} not found in database, skipping")
                continue
            
            # Upload PDFs
            uploaded_files = upload_pdfs_to_gemini(pdf_paths)
            
            if not uploaded_files:
                print(f"No files uploaded for grant {grant_id}, skipping")
                continue
            
            # Create prompt with organisation context
            prompt = f"""Review these initial grant documents against the following organisation and initiative:

ORGANISATION CONTEXT:
Name: {organisation.name}
Mission and Focus: {organisation.mission_and_focus}
About Us: {organisation.about_us}
{f"Additional Remarks: {organisation.remarks}" if organisation.remarks else ""}

INITIATIVE DETAILS:
Title: {initiative.title}
Goals: {initiative.goals}
Target Audience: {initiative.audience}
Stage: {initiative.stage}
Budget: ${initiative.costs:,}
{f"Demographic: {initiative.demographic}" if initiative.demographic else ""}
{f"Remarks: {initiative.remarks}" if initiative.remarks else ""}

Rate the relevance of this grant to the organisation's mission and this specific initiative on a scale of 0-100, where:
- 0-20: Not relevant at all
- 21-40: Slightly relevant
- 41-60: Moderately relevant
- 61-80: Highly relevant
- 81-100: Extremely relevant

Consider:
- Alignment with the organisation's overall mission and focus
- Fit with the initiative's specific goals and audience
- Appropriateness for the initiative's stage and budget
- Match with target demographic

Return ONLY the integer rating (0-100), nothing else."""
            
            try:
                # Generate response
                response = model.generate_content([prompt] + uploaded_files)
                rate_limit_sleep()
                
                # Parse rating
                rating_text = response.text.strip()
                prelim_rating = int(rating_text)
                
                # Validate rating range
                if not (0 <= prelim_rating <= 100):
                    print(f"Warning: Rating {prelim_rating} out of range, clamping")
                    prelim_rating = max(0, min(100, prelim_rating))
                
                print(f"Preliminary Rating: {prelim_rating}/100")
                
                # DIRECT DATABASE UPDATE using SQLAlchemy ORM:
                # 1. Query for existing Result row
                result = session.query(Result).filter_by(
                    grant_id=grant_id,
                    initiative_id=initiative_id
                ).first()
                
                if result:
                    # 2a. Update existing row
                    result.prelim_rating = prelim_rating
                    print(f"Updating existing Result row...")
                else:
                    # 2b. Create new Result object
                    result = Result(
                        grant_id=grant_id,
                        initiative_id=initiative_id,
                        prelim_rating=prelim_rating
                    )
                    session.add(result)
                    print(f"Creating new Result row...")
                
                # 3. Commit transaction to PostgreSQL database
                session.commit()
                print(f"✓ Saved to database (committed to PostgreSQL)")
                
            except ValueError as e:
                print(f"Error parsing rating: {e}, response was: {response.text}")
            except Exception as e:
                print(f"Error analyzing grant {grant_id}: {e}")
                # Rollback transaction on error
                session.rollback()
            
            finally:
                # Clean up uploaded files
                for uploaded_file in uploaded_files:
                    try:
                        genai.delete_file(uploaded_file.name)
                    except:
                        pass
        
        print(f"\n✓ Preliminary scan complete for initiative {initiative_id}")
        
    finally:
        session.close()


def generate_shortlist(initiative_id: int, cutoff: int = 60) -> List[int]:
    """
    Step 2: Generate shortlist of grants above the cutoff rating.
    Saves to shortlist_for_scraper.json.
    
    This function READS FROM THE DATABASE using SQLAlchemy ORM:
    - Creates a Session to query the database
    - Uses session.query() to fetch Result rows
    - Does NOT modify the database, only reads
    
    Args:
        initiative_id: ID of the initiative
        cutoff: Minimum prelim_rating to include (default 60)
        
    Returns:
        List of grant IDs in the shortlist
    """
    print(f"\n{'='*60}")
    print(f"STEP 2: Generating Shortlist for Initiative {initiative_id}")
    print(f"{'='*60}\n")
    print(f"Cutoff: {cutoff}/100\n")
    
    session = Session(engine)
    
    try:
        # Query results above cutoff (READ from database)
        results = session.query(Result).filter(
            Result.initiative_id == initiative_id,
            Result.prelim_rating > cutoff
        ).all()
        
        shortlist = [result.grant_id for result in results]
        
        print(f"Found {len(shortlist)} grants above cutoff:")
        for result in results:
            grant = session.query(Grant).filter_by(id=result.grant_id).first()
            print(f"  - Grant {result.grant_id}: {grant.name if grant else 'Unknown'} "
                  f"(Rating: {result.prelim_rating})")
        
        # Save to JSON for scraper
        shortlist_data = {
            "initiative_id": initiative_id,
            "cutoff": cutoff,
            "generated_at": datetime.now().isoformat(),
            "grant_ids": shortlist
        }
        
        with open("shortlist_for_scraper.json", "w") as f:
            json.dump(shortlist_data, f, indent=2)
        
        print(f"\n✓ Shortlist saved to shortlist_for_scraper.json")
        
        return shortlist
        
    finally:
        session.close()


def run_deep_analysis(initiative_id: int, deep_pdf_dir: str):
    """
    Step 3: Deep analysis of comprehensive grant PDFs for shortlisted grants.
    Extracts detailed information and updates Result rows.
    
    This function DIRECTLY UPDATES THE DATABASE using SQLAlchemy ORM:
    - Queries for existing Result rows that need deep analysis
    - Updates multiple fields on existing Result objects
    - Calls session.commit() to save all extracted grant data to PostgreSQL
    
    Args:
        initiative_id: ID of the initiative
        deep_pdf_dir: Directory containing comprehensive grant PDFs
    """
    print(f"\n{'='*60}")
    print(f"STEP 3: Running Deep Analysis for Initiative {initiative_id}")
    print(f"{'='*60}\n")
    
    session = Session(engine)
    
    try:
        # Get initiative details
        initiative = session.query(Initiative).filter_by(id=initiative_id).first()
        if not initiative:
            print(f"Error: Initiative {initiative_id} not found")
            return
        
        # Get organisation details
        organisation = session.query(Organisation).filter_by(id=initiative.organisation_id).first()
        if not organisation:
            print(f"Error: Organisation {initiative.organisation_id} not found")
            return
        
        # Get shortlisted grants (those with prelim_rating)
        shortlisted_results = session.query(Result).filter(
            Result.initiative_id == initiative_id,
            Result.prelim_rating.isnot(None)
        ).all()
        
        shortlisted_grant_ids = {result.grant_id for result in shortlisted_results}
        print(f"Shortlisted grants to analyze: {shortlisted_grant_ids}\n")
        
        # Scan for deep PDFs
        pdf_map = scan_folder_for_pdfs(deep_pdf_dir)
        
        if not pdf_map:
            print(f"No PDFs found in {deep_pdf_dir}")
            return
        
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Process each grant
        for grant_id, pdf_paths in pdf_map.items():
            # Validate grant is in shortlist
            if grant_id not in shortlisted_grant_ids:
                print(f"Skipping grant {grant_id} - not in shortlist")
                continue
            
            print(f"\n--- Deep Analysis: Grant ID {grant_id} ---")
            
            grant = session.query(Grant).filter_by(id=grant_id).first()
            if not grant:
                print(f"Warning: Grant {grant_id} not found in database")
                continue
            
            print(f"Grant: {grant.name}")
            
            # Upload PDFs
            uploaded_files = upload_pdfs_to_gemini(pdf_paths)
            
            if not uploaded_files:
                print(f"No files uploaded for grant {grant_id}, skipping")
                continue
            
            # Create detailed analysis prompt with organisation context
            prompt = f"""Analyze these comprehensive grant documents in detail for the following organisation and initiative:

ORGANISATION CONTEXT:
Name: {organisation.name}
Mission and Focus: {organisation.mission_and_focus}
About Us: {organisation.about_us}
{f"Additional Remarks: {organisation.remarks}" if organisation.remarks else ""}

INITIATIVE DETAILS:
Title: {initiative.title}
Goals: {initiative.goals}
Target Audience: {initiative.audience}
Stage: {initiative.stage}
Budget: ${initiative.costs:,}
{f"Demographic: {initiative.demographic}" if initiative.demographic else ""}
{f"Remarks: {initiative.remarks}" if initiative.remarks else ""}

Extract and return ONLY a valid JSON object with the following structure:
{{
  "grant_description": "Brief description of what this grant funds (2-3 sentences)",
  "criteria": ["criterion 1", "criterion 2", "criterion 3"],
  "grant_amount": "Funding amount or range (e.g., '$50,000 - $100,000' or 'Up to $250,000')",
  "match_rating": 85,
  "uncertainty_rating": 15,
  "deadline": "2025-03-15T00:00:00",
  "sources": ["page 1", "page 3", "section 2.1"],
  "explanations": {{
    "alignment": "Explanation of how grant aligns with organisation mission and initiative goals",
    "strengths": "Key strengths of this match for both organisation and initiative",
    "concerns": "Any concerns or weaknesses regarding fit",
    "recommendations": "Recommendations for application strategy"
  }}
}}

Guidelines:
- match_rating: 0-100 score for overall match quality considering both organisation mission and initiative specifics
- uncertainty_rating: 0-100 score for confidence (higher = more uncertain)
- deadline: ISO format datetime or null if not found
- criteria: List of eligibility criteria as strings
- sources: Where you found key information
- Consider both the organisation's broader mission AND the specific initiative's needs
- Return ONLY valid JSON, no markdown formatting, no explanation text"""
            
            try:
                # Generate response
                response = model.generate_content([prompt] + uploaded_files)
                rate_limit_sleep()
                
                # Parse JSON response
                response_text = response.text.strip()
                # Remove markdown code blocks if present
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                analysis_data = json.loads(response_text)
                
                print(f"Match Rating: {analysis_data.get('match_rating')}/100")
                print(f"Uncertainty: {analysis_data.get('uncertainty_rating')}/100")
                print(f"Grant Amount: {analysis_data.get('grant_amount')}")
                
                # Parse deadline if present
                deadline = None
                if analysis_data.get('deadline'):
                    try:
                        deadline = datetime.fromisoformat(analysis_data['deadline'].replace('Z', '+00:00'))
                    except:
                        pass
                
                # DIRECT DATABASE UPDATE:
                # 1. Query for existing Result row
                result = session.query(Result).filter_by(
                    grant_id=grant_id,
                    initiative_id=initiative_id
                ).first()
                
                if result:
                    # 2. Update all deep analysis fields on the Result object
                    result.grant_description = analysis_data.get('grant_description')
                    result.criteria = analysis_data.get('criteria')
                    result.grant_amount = analysis_data.get('grant_amount')
                    result.match_rating = analysis_data.get('match_rating')
                    result.uncertainty_rating = analysis_data.get('uncertainty_rating')
                    result.deadline = deadline
                    result.sources = analysis_data.get('sources')
                    result.explanations = analysis_data.get('explanations')
                    
                    # 3. Commit changes to PostgreSQL
                    session.commit()
                    print(f"✓ Updated database with deep analysis (committed to PostgreSQL)")
                else:
                    print(f"Warning: No existing Result row found for grant {grant_id}")
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                print(f"Response was: {response.text[:500]}")
            except Exception as e:
                print(f"Error analyzing grant {grant_id}: {e}")
                session.rollback()
            
            finally:
                # Clean up uploaded files
                for uploaded_file in uploaded_files:
                    try:
                        genai.delete_file(uploaded_file.name)
                    except:
                        pass
        
        print(f"\n✓ Deep analysis complete for initiative {initiative_id}")
        
    finally:
        session.close()


def export_results_to_frontend(initiative_id: int):
    """
    Step 4: Export fully analyzed results to frontend JSON file.
    
    This function READS FROM THE DATABASE using SQLAlchemy ORM:
    - Queries Result rows with completed deep analysis
    - Does NOT modify the database, only reads and exports to JSON
    
    Args:
        initiative_id: ID of the initiative
    """
    print(f"\n{'='*60}")
    print(f"STEP 4: Exporting Results for Initiative {initiative_id}")
    print(f"{'='*60}\n")
    
    session = Session(engine)
    
    try:
        # Query all results with deep analysis (READ from database)
        results = session.query(Result).filter(
            Result.initiative_id == initiative_id,
            Result.match_rating.isnot(None)
        ).all()
        
        print(f"Found {len(results)} fully analyzed grants\n")
        
        # Convert to dictionaries
        export_data = []
        
        for result in results:
            grant = session.query(Grant).filter_by(id=result.grant_id).first()
            
            result_dict = {
                "grant_id": result.grant_id,
                "grant_name": grant.name if grant else "Unknown",
                "grant_url": grant.url if grant else "",
                "initiative_id": result.initiative_id,
                "prelim_rating": result.prelim_rating,
                "grant_description": result.grant_description,
                "criteria": result.criteria,
                "grant_amount": result.grant_amount,
                "match_rating": result.match_rating,
                "uncertainty_rating": result.uncertainty_rating,
                "deadline": result.deadline.isoformat() if result.deadline else None,
                "sources": result.sources,
                "explanations": result.explanations
            }
            
            export_data.append(result_dict)
            
            print(f"  ✓ Grant {result.grant_id}: {grant.name if grant else 'Unknown'} "
                  f"(Match: {result.match_rating}/100)")
        
        # Save to JSON
        output = {
            "initiative_id": initiative_id,
            "exported_at": datetime.now().isoformat(),
            "total_results": len(export_data),
            "results": export_data
        }
        
        with open("frontend_data.json", "w") as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✓ Results exported to frontend_data.json")
        
    finally:
        session.close()


if __name__ == "__main__":
    """
    Main execution: Run the full pipeline in order.
    """
    print("\n" + "="*60)
    print("GRANT MATCHING AI ANALYSIS PIPELINE")
    print("="*60)
    
    INITIATIVE_ID = 1
    PRELIM_CUTOFF = 70
    
    # Step 1: Preliminary Scan
    run_prelim_scan(INITIATIVE_ID, "downloads/initial_scrape")
    
    # Step 2: Generate Shortlist
    shortlist = generate_shortlist(INITIATIVE_ID, cutoff=PRELIM_CUTOFF)
    
    # Simulate pause for deep scraper
    print("\n" + "="*60)
    print("⏸️  PIPELINE PAUSED")
    print("="*60)
    print("\nWaiting for teammate's Deep Scraper to collect comprehensive PDFs...")
    print(f"Scraper should process grant_ids: {shortlist}")
    print("\nSimulating pause for Deep Scraper...")
    print("(In production, the scraper would run here based on shortlist_for_scraper.json)\n")
    time.sleep(2)  # Symbolic pause
    
    # Step 3: Deep Analysis
    run_deep_analysis(INITIATIVE_ID, "downloads/deep_scrape")
    
    # Step 4: Export Results
    export_results_to_frontend(INITIATIVE_ID)
    
    print("\n" + "="*60)
    print("✓ PIPELINE COMPLETE")
    print("="*60)
    print("\nOutputs generated:")
    print("  1. shortlist_for_scraper.json - For deep scraper")
    print("  2. frontend_data.json - For frontend display")
    print("\nDatabase updated with:")
    print("  - Preliminary ratings (Step 1)")
    print("  - Detailed analysis (Step 3)")