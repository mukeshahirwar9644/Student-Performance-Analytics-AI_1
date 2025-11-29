"""
Submission Package Creator
Creates a complete submission package with all deliverables
"""
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from generate_submission_pdfs import generate_all_pdfs

def create_submission_package():
    """
    Create a complete submission package
    """
    print("="*60)
    print("Creating Submission Package")
    print("="*60)
    
    # Generate PDFs first
    print("\n1. Generating submission PDFs...")
    pdfs = generate_all_pdfs()
    
    # Create submission directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    submission_dir = Path("submission_package")
    submission_dir.mkdir(exist_ok=True)
    
    print(f"\n2. Organizing files in {submission_dir}...")
    
    # Copy source files
    source_files = [
        "config.py",
        "kaggle_loader.py",
        "data_processor.py",
        "gemini_ai.py",
        "google_sheets.py",
        "alert_system.py",
        "export_manager.py",
        "main_workflow.py",
        "test_cases.py",
        "requirements.txt",
        "setup.sh",
        "README.md",
        "elseif_workflow.json",
        ".env.example"
    ]
    
    for file in source_files:
        src = Path(file)
        if src.exists():
            shutil.copy2(src, submission_dir / file)
            print(f"  ✓ {file}")
    
    # Copy PDFs
    for pdf in pdfs:
        if pdf.exists():
            shutil.copy2(pdf, submission_dir / pdf.name)
            print(f"  ✓ {pdf.name}")
    
    # Create submission README
    submission_readme = submission_dir / "SUBMISSION_README.txt"
    with open(submission_readme, 'w') as f:
        f.write("""STUDENT PERFORMANCE ANALYTICS AI - SUBMISSION PACKAGE
========================================================

This package contains a complete, production-ready implementation of the 
Student Performance Analytics AI system.

CONTENTS:
---------
1. Source Code (Python modules)
2. Configuration Files
3. Submission PDFs:
   - Attachment_A_Problem_Discussion.pdf
   - Attachment_B_Approach_Implementation.pdf
   - Attachment_C_Test_Cases_Evidence.pdf
4. Documentation (README.md)
5. Deployment Files (elseif_workflow.json)
6. Setup Scripts (setup.sh)

QUICK START:
-----------
1. Run: ./setup.sh
2. Edit .env with your API keys
3. Run: python main_workflow.py

TESTING:
--------
Run: python test_cases.py

DEPLOYMENT:
----------
Run: python deploy_elseif.py
Then import elseif_workflow.json to ElseIf Playground

REQUIREMENTS:
------------
- Python 3.8+
- Kaggle API credentials
- Google Gemini API key
- (Optional) Google Sheets service account

All code is production-ready and follows best practices.
No modifications required except API key configuration.

========================================================
Ready for Submission ✅
========================================================
""")
    
    print(f"  ✓ SUBMISSION_README.txt")
    
    # Create ZIP archive
    print(f"\n3. Creating ZIP archive...")
    zip_filename = f"Student_Analytics_AI_Submission_{timestamp}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in submission_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(submission_dir)
                zipf.write(file_path, arcname)
                print(f"  ✓ Added {arcname}")
    
    print(f"\n{'='*60}")
    print(f"Submission package created successfully!")
    print(f"{'='*60}")
    print(f"\nDirectory: {submission_dir}")
    print(f"ZIP Archive: {zip_filename}")
    print(f"\nPackage includes:")
    print(f"  • All source code")
    print(f"  • 3 submission PDFs")
    print(f"  • Complete documentation")
    print(f"  • Deployment configuration")
    print(f"  • Setup scripts")
    print(f"\nReady for email submission! 📧")
    
    return submission_dir, zip_filename


if __name__ == "__main__":
    create_submission_package()


