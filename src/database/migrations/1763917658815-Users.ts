import { MigrationInterface, QueryRunner } from "typeorm";

export class Users1763917658815 implements MigrationInterface {
    name = 'Users1763917658815'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`CREATE TYPE "public"."users_role_enum" AS ENUM('ADMIN', 'EMPLOYEE')`);
        await queryRunner.query(`CREATE TABLE "users" ("id" BIGSERIAL NOT NULL, "name" character varying(70) NOT NULL, "email" character varying NOT NULL, "password" character varying(70) NOT NULL, "role" "public"."users_role_enum" NOT NULL, "reports_to" bigint NOT NULL, "team_id" bigint NOT NULL, "project_id" bigint, CONSTRAINT "UQ_97672ac88f789774dd47f7c8be3" UNIQUE ("email"), CONSTRAINT "PK_a3ffb1c0c8416b9fc6f907b7433" PRIMARY KEY ("id"))`);
        await queryRunner.query(`ALTER TABLE "users" ADD CONSTRAINT "FK_1208ee1db5ddb64b48a86b46a61" FOREIGN KEY ("team_id") REFERENCES "teams"("id") ON DELETE NO ACTION ON UPDATE NO ACTION`);
        await queryRunner.query(`ALTER TABLE "users" ADD CONSTRAINT "FK_22b2bcb031a944b0859d5afd0b2" FOREIGN KEY ("project_id") REFERENCES "projects"("id") ON DELETE NO ACTION ON UPDATE NO ACTION`);
        await queryRunner.query(`ALTER TABLE "users" ADD "joining_date" TIMESTAMP NOT NULL DEFAULT now()`);
        await queryRunner.query(`ALTER TABLE "users" ADD CONSTRAINT "FK_87ac9a33f6cb47b2d362c308eae" FOREIGN KEY ("reports_to") REFERENCES "managers"("id") ON DELETE NO ACTION ON UPDATE NO ACTION`);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`ALTER TABLE "users" DROP CONSTRAINT "FK_22b2bcb031a944b0859d5afd0b2"`);
        await queryRunner.query(`ALTER TABLE "users" DROP CONSTRAINT "FK_1208ee1db5ddb64b48a86b46a61"`);
        await queryRunner.query(`ALTER TABLE "users" DROP CONSTRAINT "FK_87ac9a33f6cb47b2d362c308eae"`);
        await queryRunner.query(`ALTER TABLE "users" DROP COLUMN "joining_date"`);
        await queryRunner.query(`DROP TABLE "users"`);
    }

}
