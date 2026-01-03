import { MigrationInterface, QueryRunner } from "typeorm";

export class Managers1763917598589 implements MigrationInterface {
    name = 'Managers1763917598589'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`CREATE TABLE "managers" ("id" BIGSERIAL NOT NULL, "name" character varying(70) NOT NULL, "email" character varying NOT NULL, CONSTRAINT "UQ_8d5fd9a2217bf7b16bef11fdf83" UNIQUE ("email"), CONSTRAINT "PK_e70b8cc457276d9b4d82342a8ff" PRIMARY KEY ("id"))`);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP TABLE "managers"`);
      
    }

}
