import { MigrationInterface, QueryRunner } from "typeorm";

export class ProjectsManager1763917672084 implements MigrationInterface {
    name = 'ProjectsManager1763917672084'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`CREATE TABLE "project_managers" ("project_id" bigint NOT NULL, "manager_id" bigint NOT NULL, CONSTRAINT "PK_4aed6230dd243b85b6da5e78470" PRIMARY KEY ("project_id", "manager_id"))`);
        await queryRunner.query(`CREATE INDEX "IDX_3e77979428981f491856c6e74f" ON "project_managers" ("project_id") `);
        await queryRunner.query(`CREATE INDEX "IDX_f6fcbf91907b2f5a59c91133cc" ON "project_managers" ("manager_id") `);
        await queryRunner.query(`ALTER TABLE "project_managers" ADD CONSTRAINT "FK_3e77979428981f491856c6e74fc" FOREIGN KEY ("project_id") REFERENCES "projects"("id") ON DELETE CASCADE ON UPDATE CASCADE`);
        await queryRunner.query(`ALTER TABLE "project_managers" ADD CONSTRAINT "FK_f6fcbf91907b2f5a59c91133cce" FOREIGN KEY ("manager_id") REFERENCES "managers"("id") ON DELETE NO ACTION ON UPDATE NO ACTION`);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`ALTER TABLE "project_managers" DROP CONSTRAINT "FK_f6fcbf91907b2f5a59c91133cce"`);
        await queryRunner.query(`ALTER TABLE "project_managers" DROP CONSTRAINT "FK_3e77979428981f491856c6e74fc"`);
        await queryRunner.query(`DROP TABLE "project_managers"`);
    }

}
